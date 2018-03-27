import argparse
import os
import sys

from infraboxcli.graph import graph
from infraboxcli.init import init
from infraboxcli.list_jobs import list_jobs
from infraboxcli.log import logger
from infraboxcli.pull import pull
from infraboxcli.push import push
from infraboxcli.run import run
from infraboxcli.validate import validate

from infraboxcli.dashboard import user
from infraboxcli.dashboard import project

version = '0.6.2'

def main():
    username = 'unknown'

    if os.name != 'nt':
        import pwd
        username = pwd.getpwuid(os.getuid()).pw_name

    parser = argparse.ArgumentParser(prog="infrabox")
    parser.add_argument("--url",
                        required=False,
                        default=os.environ.get('INFRABOX_URL', None),
                        help="Address of the API server")
    parser.add_argument("--ca-bundle",
                        required=False,
                        default=os.environ.get('INFRABOX_CA_BUNDLE', None),
                        help="Path to a CA_BUNDLE file or directory with certificates of trusted CAs")
    parser.add_argument("-f", dest='infrabox_json_file', required=False, type=str,
                        help="Path to an infrabox.json file")
    sub_parser = parser.add_subparsers(help='sub-command help')

    # version
    version_init = sub_parser.add_parser('version', help='Show the current version')
    version_init.set_defaults(version=version)

    # init
    parser_init = sub_parser.add_parser('init', help='Create a simple project')
    parser_init.set_defaults(is_init=True)
    parser_init.set_defaults(func=init)

    # push
    parser_push = sub_parser.add_parser('push', help='Push a local project to InfraBox')
    parser_push.add_argument("--show-console", action='store_true', required=False,
                             help="Show the console output of the jobs")
    parser_push.set_defaults(show_console=False)
    parser_push.set_defaults(validate_only=False)
    parser_push.set_defaults(func=push)

    # pull
    parser_pull = sub_parser.add_parser('pull', help='Pull a remote job')
    parser_pull.set_defaults(is_pull=True)
    parser_pull.add_argument("--job-id", required=True)
    parser_pull.add_argument("--no-container", required=False, dest='pull_container', action='store_false',
                             help="Only the inputs will be downloaded but not the actual container. Implies --no-run.")
    parser_pull.set_defaults(pull_container=True)

    parser_pull.add_argument("--no-run", required=False, dest='run_container', action='store_false',
                             help="The container will not be run.")
    parser_pull.set_defaults(run_container=True)
    parser_pull.set_defaults(func=pull)

    # graph
    parser_graph = sub_parser.add_parser('graph', help='Generate a graph of your local jobs')
    parser_graph.add_argument("--output", required=True, type=str,
                              help="Path to the output file")
    parser_graph.set_defaults(func=graph)

    # validate
    validate_graph = sub_parser.add_parser('validate', help='Validate infrabox.json')
    validate_graph.set_defaults(func=validate)

    # list
    list_job = sub_parser.add_parser('list', help='List all available jobs')
    list_job.set_defaults(func=list_jobs)

    # run
    parser_run = sub_parser.add_parser('run', help='Run your jobs locally')
    parser_run.add_argument("job_name", nargs="?", type=str,
                            help="Job name to execute")
    parser_run.add_argument("--no-rm", action='store_true', required=False,
                            help="Does not run 'docker-compose rm' before building")
    parser_run.add_argument("-t", dest='tag', required=False, type=str,
                            help="Docker image tag")
    parser_run.add_argument("-c", "--children", action='store_true',
                            help="Also run children of a job")
    parser_run.add_argument("--local-cache", required=False, type=str,
                            default="/tmp/{}/infrabox/local-cache".format(username),
                            help="Path to the local cache")

    parser_run.set_defaults(no_rm=False)
    parser_run.set_defaults(func=run)

    # Collaborators
    parser_collaborators = sub_parser.add_parser('collaborators', help='Add or remove collaborators for your project')
    sub_collaborators = parser_collaborators.add_subparsers()

    parser_add_collaborator = sub_collaborators.add_parser('add', help='Add collaborator')
    parser_add_collaborator.add_argument('--username', required=True, type=str,
                                         help='Username of collaborator you want to add')
    parser_add_collaborator.set_defaults(func=project.add_collaborator)

    parser_remove_collaborator = sub_collaborators.add_parser('remove', help='Remove collaborator')
    parser_remove_collaborator.add_argument('--username', required=True, type=str,
                                         help='Username of collaborator you want to remove')
    parser_remove_collaborator.set_defaults(func=project.remove_collaborator)

    # Secrets
    parser_secrets = sub_parser.add_parser('secrets', help='Create or delete secrets')
    sub_secrets = parser_secrets.add_subparsers()

    parser_create_secret = sub_secrets.add_parser('create', help='Create secret')
    parser_create_secret.add_argument('--name', required=True, type=str, help='Name of your new secret')
    parser_create_secret.add_argument('--value', required=True, type=str, help='Value of your new secret')
    parser_create_secret.set_defaults(func=project.add_secret)

    parser_delete_secret = sub_secrets.add_parser('delete', help='Delete secret')
    parser_delete_secret.add_argument('--name', required=True, type=str, help='Name of secret you want to delete')
    parser_delete_secret.set_defaults(func=project.delete_secret)

    # Tokens
    parsers_project_tokens = sub_parser.add_parser('project-token', help='Manage your project tokens')
    sub_project_tokens = parsers_project_tokens.add_subparsers()

    parser_add_project_token = sub_project_tokens.add_parser('add', help='Add project token')
    parser_add_project_token.add_argument('--d', required=True, type=str,
                                          help='Description of project token you want to add')
    parser_add_project_token.add_argument('--scope_push', required=False, action='store_true',
                                          help='Scope push')
    parser_add_project_token.add_argument('--scope_pull', required=False, action='store_true',
                                          help='Scope pull')
    parser_add_project_token.set_defaults(func=project.add_token)

    parser_remove_project_token = sub_project_tokens.add_parser('remove', help='Remove project token')
    parser_remove_project_token.add_argument('--id', required=True, type=str,
                                             help='Id of project token you want to remove')
    parser_remove_project_token.set_defaults(func=project.delete_token)

    # User
    parser_login = sub_parser.add_parser('login', help='Login to infrabox')
    parser_login.set_defaults(func=user.login)

    # Parse args
    args = parser.parse_args()

    if 'version' in args:
        print('infraboxcli %s' % version)
        return

    if "DOCKER_HOST" in os.environ:
        logger.error("DOCKER_HOST is set")
        logger.error("infrabox can't be used to run jobs on a remote machine")
        sys.exit(1)

    if args.ca_bundle:
        if args.ca_bundle.lower() == "false":
            args.ca_bundle = False
        else:
            if not os.path.exists(args.ca_bundle):
                logger.error("INFRABOX_CA_BUNDLE: %s not found" % args.ca_bundle)
                sys.exit(1)

    # Find infrabox.json
    p = os.getcwd()

    while p:
        tb = os.path.join(p, 'infrabox.json')
        if not os.path.exists(tb):
            p = p[0:p.rfind('/')]
        else:
            args.project_root = p
            args.infrabox_json = tb
            args.project_name = os.path.basename(p)
            break

    if 'job_name' not in args:
        args.children = True

    if 'project_root' not in args and 'is_init' not in args and 'is_pull' not in args:
        logger.error("infrabox.json not found in current or any parent directory")
        sys.exit(1)

    if args.infrabox_json_file:
        args.infrabox_json = args.infrabox_json_file

    # Run command
    args.func(args)
