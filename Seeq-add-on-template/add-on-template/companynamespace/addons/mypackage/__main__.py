import os
import re
import sys
import argparse
import subprocess
from getpass import getpass
from packaging import version
from urllib.parse import urlparse, urlunparse
import seeq
from seeq import sdk, spy
from seeq.sdk.rest import ApiException
from ._copy import copy

DATA_LAB_PROJECT_ID_REGEX = r'.*/data-lab/([0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}).*'
NB_EXTENSIONS = ['widgetsnbextension', 'plotlywidget', 'ipyvuetify', 'ipyvue']
DEPLOYMENT_FOLDER = 'deployment'
DEPLOYMENT_NOTEBOOK = "my_addon_master.ipynb"


def sanitize_sdl_url(url):
    parsed = urlparse(url)
    project_id_search = re.search(DATA_LAB_PROJECT_ID_REGEX, url, re.IGNORECASE)
    if parsed.scheme == '' or parsed.netloc == '' or parsed.path == '':
        raise ValueError(f"The SDL_url should have the format "
                         f"https://my.seeq.com/data-lab/6AB49411-917E-44CC-BA19-5EE0F903100C/ but got {url}")
    if project_id_search is None:
        raise ValueError(f"Invalid URL. Could not find data-lab project ID. Got URL: {url}")
    id = project_id_search.group(1)
    return urlunparse(parsed).strip(" ").split(id)[0] + id


def permissions_defaults(permissions_group: list, permissions_users: list):
    if permissions_group is None:
        permissions_group = ['Everyone']

    if permissions_users is None:
        permissions_users = []
    return permissions_group, permissions_users


def install_app(sdl_url_, *, sort_key=None, permissions_group: list = None, permissions_users: list = None):
    """
    Installs MyFirstAddOn as an Add-on Tool in Seeq Workbench

    Parameters
    ----------
    sdl_url_: str
        URL of the SDL container.
        E.g. https://my.seeq.com/data-lab/6AB49411-917E-44CC-BA19-5EE0F903100C/
    sort_key: str, default None
        A string, typically one character letter. The sort_key determines the
        order in which the Add-on Tools are displayed in the tool panel
    permissions_group: list
        Names of the Seeq groups that will have access to each tool
    permissions_users: list
        Names of Seeq users that will have access to each tool
    Returns
    --------
    -: None
        MyFirstAddOn will appear as Add-on Tool(s) in Seeq
        Workbench
    """

    sdl_url_ = sanitize_sdl_url(sdl_url_)

    if sort_key is None:
        sort_key = 'a'

    permissions_group, permissions_users = permissions_defaults(permissions_group, permissions_users)

    add_on_details = dict(
        name='My First Add-on',
        description="Simple math with signals",
        iconClass="fa fa-th",
        targetUrl=f'{sdl_url_}/apps/{DEPLOYMENT_FOLDER}/{DEPLOYMENT_NOTEBOOK}?'
                  f'workbookId={{workbookId}}&worksheetId={{worksheetId}}',
        linkType="window",
        windowDetails="toolbar=0,location=0,left=800,top=400,height=1000,width=1400",
        sortKey=sort_key,
        reuseWindow=True,
        permissions=dict(groups=permissions_group,
                         users=permissions_users)
    )

    copy(des_folder=DEPLOYMENT_FOLDER, src_folder='mypackage/deployment_notebook',
         overwrite_folder=False, overwrite_contents=True)
    add_on_tool_management(add_on_details)


def print_red(text): print(f"\x1b[31m{text}\x1b[0m")


def get_datalab_project_id(target_url, items_api):
    project_id_search = re.search(DATA_LAB_PROJECT_ID_REGEX, target_url, re.IGNORECASE)
    if project_id_search:
        data_lab_project_id = project_id_search.group(1)
        try:
            items_api.get_item_and_all_properties(id=data_lab_project_id)
            return data_lab_project_id
        except Exception as error:
            print_red(error.body)


def add_datalab_project_ace(data_lab_project_id, ace_input, items_api):
    if data_lab_project_id:
        try:
            items_api.add_access_control_entry(id=data_lab_project_id, body=ace_input)
        except Exception as error:
            print_red(error.body)


def get_user_group(group_name, user_groups_api):
    try:
        group = user_groups_api.get_user_groups(name_search=group_name)
        assert len(group.items) != 0, 'No group named "%s" was found' % group_name
        assert len(group.items) == 1, 'More that one group named "%s" was found' % group_name
        return group
    except AssertionError as error:
        print_red(error)
    except ApiException as error:
        print_red(error.body)


def get_user(user_name, users_api):
    try:
        user_ = users_api.get_users(username_search=user_name)
        if len(user_.users) == 0:
            raise ValueError(f'No user named {user_name} was found')
        if len(user_.users) > 1:
            raise ValueError(f'More than one user named {user_name} was found')
        return user_
    except AssertionError as error:
        print_red(error)
    except ApiException as error:
        print_red(error.body)


def add_on_tool_management(my_tool_config):
    system_api = sdk.SystemApi(spy.client)
    users_api = sdk.UsersApi(spy.client)
    user_groups_api = sdk.UserGroupsApi(spy.client)
    items_api = sdk.ItemsApi(spy.client)
    tools_api_name = get_tools_api_name()
    tools = None
    if tools_api_name == 'external':
        tools = system_api.get_external_tools().external_tools
    elif tools_api_name == 'add_on':
        # TODO: Needs updated API call once the SDK is released
        tools = system_api.get_add_on_tools().add_on_tools
    # Define add-on tools to be added
    # ?workbookId={workbookId}&worksheetId={worksheetId}&workstepId={workstepId}&seeqVersion={seeqVersion}
    # First, do no harm.
    # This extracts the tools that are already there.
    # You can then either modify an item or add to this list.
    tools_config = list()
    for tool in tools:
        tools_config.append({
            "name": tool.name,
            "description": tool.description,
            "iconClass": tool.icon_class,
            "targetUrl": tool.target_url,
            "linkType": tool.link_type,
            "windowDetails": tool.window_details,
            "sortKey": tool.sort_key,
            "reuseWindow": tool.reuse_window,
            "permissions": {
                "groups": list(),
                "users": list()
            }
        })
        tool_acl = items_api.get_access_control(id=tool.id)
        for ace in tool_acl.entries:
            identity = ace.identity
            if identity.type.lower() == "user":
                tools_config[-1]["permissions"]["users"].append(identity.username)
            elif identity.type.lower() == "usergroup":
                tools_config[-1]["permissions"]["groups"].append(identity.name)

    # If the tool is in the list, update it
    if my_tool_config["name"] in [t["name"] for t in tools_config]:
        list_index = [t["name"] for t in tools_config].index(my_tool_config["name"])
        tools_config[list_index].update(my_tool_config)
    # if the tool is not in the list, add it
    else:
        tools_config.append(my_tool_config)

    # Delete all existing add-on tools (only deletes the tools, not what they point to)
    for tool in tools:
        if tools_api_name == 'external':
            system_api.delete_external_tool(id=tool.id)
        elif tools_api_name == 'add_on':
            # TODO: Needs updated API call once the SDK is released
            system_api.delete_add_on_tool(id=tool.id)

    # Add add-on tools and assign add-on tool and data lab permissions to groups and users

    for tool_with_permissions in tools_config:
        # Create add-on tool
        tool = tool_with_permissions.copy()
        tool.pop("permissions")
        if tools_api_name == 'external':
            tool_id = system_api.create_external_tool(body=tool).id
        elif tools_api_name == 'add_on':
            # TODO: Needs updated API call once the SDK is released
            tool_id = system_api.create_add_on_tool(body=tool).id
        else:
            tool_id = None

        print(tool["name"])
        print(f'Add-on Tool ID - {tool_id}')
        data_lab_project_id = get_datalab_project_id(tool["targetUrl"], items_api)
        if data_lab_project_id:
            print("Target Data Lab Project ID - %s" % data_lab_project_id)
        else:
            print("TargetUrl does not reference a Data Lab project")

        # assign group permissions to add-on tool and data lab project
        groups = tool_with_permissions["permissions"]["groups"]
        for group_name in groups:
            group = get_user_group(group_name, user_groups_api)
            if group:
                ace_input = {'identityId': group.items[0].id, 'permissions': {'read': True}}
                # Add permissions to add-on tool item
                items_api.add_access_control_entry(id=tool_id, body=ace_input)
                # Add permissions to data lab project if target URL references one
                ace_input['permissions']['write'] = True  # Data lab project also needs write permission
                add_datalab_project_ace(data_lab_project_id, ace_input, items_api)
        print("Groups:", end=" "), print(*groups, sep=", ")

        # assign user permissions to add-on tool and data lab project
        users = tool_with_permissions["permissions"]["users"]
        for user_name in users:
            user = get_user(user_name, users_api)
            if user:
                ace_input = {'identityId': user.users[0].id, 'permissions': {'read': True}}
                items_api.add_access_control_entry(id=tool_id, body=ace_input)
                # Add permissions to data lab project if target URL references one
                ace_input['permissions']['write'] = True  # Data lab project also needs write permission
                add_datalab_project_ace(data_lab_project_id, ace_input, items_api)
        print("Users:", end=" "), print(*users, sep=", ")


def install_nbextensions():
    for extension in NB_EXTENSIONS:
        subprocess.run(f'jupyter nbextension install --user --py {extension}', cwd=os.path.expanduser('~'), shell=True,
                       check=True)
        subprocess.run(f'jupyter nbextension enable --user --py {extension}', cwd=os.path.expanduser('~'), shell=True,
                       check=True)


def get_tools_api_name():
    server_version = version.parse(spy.server_version)
    if server_version > version.parse(f"R{seeq.__version__}"):
        raise RuntimeError(f"The SPy module version doesn't match the Seeq server version. "
                           f"Please update the SPy module to version ~={spy.server_version.split('-')[0]}")

    if server_version < version.parse('R52.1.5'):
        return 'external'
    elif version.parse('R52.1.5') <= server_version < version.parse('R53'):
        return 'add_on'
    elif version.parse('R53') <= server_version < version.parse('R53.0.2'):
        return 'external'
    elif server_version >= version.parse('R53.0.2'):
        return 'add_on'


def cli_interface():
    """ Installs MyFirstAddOn as a Seeq Add-on Tool """
    parser = argparse.ArgumentParser(description='Install MyFirstAddOn as a Seeq Add-on Tool')
    parser.add_argument('--nbextensions_only', action='store_true',
                        help='Only installs the nbextensions without installing or updating the Add-on Tools'
                             'links')
    parser.add_argument('--username', type=str,
                        help='Username or Access Key of Seeq admin user installing the tool(s) ')
    parser.add_argument('--seeq_url', type=str, nargs='?',
                        help="Seeq hostname URL with the format https://my.seeq.com/ or https://my.seeq.com:34216")
    parser.add_argument('--users', type=str, nargs='*', default=[],
                        help="List of the Seeq users to will have access to the MyFirstAddOn Add-on Tool,"
                             " default: %(default)s")
    parser.add_argument('--groups', type=str, nargs='*', default=['Everyone'],
                        help="List of the Seeq groups to will have access to the MyFirstAddOn Add-on Tool, "
                             "default: %(default)s")
    return parser.parse_args()


if __name__ == '__main__':

    args = cli_interface()

    if args.nbextensions_only:
        print("\n\nInstalling and enabling nbextensions")
        install_nbextensions()
        sys.exit(0)
    user = args.username
    if user is None:
        user = input("\nAccess Key or Username: ")

    passwd = getpass("Access Key Password: ")
    spy.login(username=user, password=passwd, ignore_ssl_errors=True)
    seeq_url = args.seeq_url
    if seeq_url is None:
        seeq_url = input(f"\n Seeq base URL [{spy.client.host.split('/api')[0]}]: ")
        if seeq_url == '':
            seeq_url = spy.client.host.split('/api')[0]
    url_parsed = urlparse(seeq_url)
    seeq_url_base = f"{url_parsed.scheme}://{url_parsed.netloc}"

    project_id = spy.utils.get_data_lab_project_id()
    sdl_url = f'{seeq_url_base}/data-lab/{project_id}'
    if project_id is None:
        print("\nThe project ID could not be found. Please provide the SDL project URL with the format "
              "https://my.seeq.com/data-lab/6AB49411-917E-44CC-BA19-5EE0F903100C/\n")
        sdl_url = input("Seeq Data Lab project URL: ")
        project_id = get_datalab_project_id(sanitize_sdl_url(sdl_url), sdk.ItemsApi(spy.client))
        if not project_id:
            raise RuntimeError(f'Could not install {args.apps} because the SDL project ID could not be found')
    sdl_url_sanitized = sanitize_sdl_url(sdl_url)

    print(f"\nThe MyFirstAddOn Tool will be installed on the SDL notebook: {sdl_url_sanitized}\n"
          f"If this is not your intent, you can quit the installation now ")
    print('\n[enter] to continue or type "quit" to exit installation')
    choice = None
    while choice != '' and choice != 'quit':
        choice = input()
        if choice == '':
            print("\n\nInstalling and enabling nbextensions")
            install_nbextensions()
            install_app(sdl_url_sanitized, permissions_group=args.groups, permissions_users=args.users)
        elif choice == 'quit':
            print("\nExited installation")
        else:
            print(f'\nCommand "{choice}" is not valid')
            print('\n[enter] to continue the installation or type "quit" to exit installation')
