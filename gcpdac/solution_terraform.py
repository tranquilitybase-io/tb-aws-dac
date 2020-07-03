# Copyright 2019 The Tranquility Base Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json

from python_terraform import Terraform

import config
from gcpdac.shell_utils import create_repo, delete_repo
from gcpdac.terraform_utils import terraform_apply, terraform_destroy, terraform_init, NOT_USED_ON_DESTROY
from gcpdac.utils import labellize, random_element, sanitize

logger = config.logger


def create_solution(solutiondata):

    logger.info("Calling Jenkins")
    call_string = "curl http://{jenkins_server}/jenkins/git/notifyCommit?url={git_repo_url}".format(
    git_repo_url=git_repo_url,
    jenkins_server=jenkins_server)
    TODO this is a hard-coded jenkins server! just for demo, remove soon after
    call_string = "curl -X POST jenkins stuff"
    call_process(call_string)


def delete_solution(solutiondata):
    tf_data = dict()
    solution_id = solutiondata.get("id")
    logger.debug("solution_id is %s", solution_id)

    tf_data['cost_centre'] = NOT_USED_ON_DESTROY
    tf_data['business_unit'] = NOT_USED_ON_DESTROY
    tf_data['deployment_folder_id'] = NOT_USED_ON_DESTROY
    tf_data['environments'] = list()
    tf_data['solution_name'] = NOT_USED_ON_DESTROY
    tf_data['random_element'] = NOT_USED_ON_DESTROY
    tf_data['region'] = NOT_USED_ON_DESTROY
    tf_data['region_zone'] = NOT_USED_ON_DESTROY
    tf_data['tb_discriminator'] = NOT_USED_ON_DESTROY
    tf_data['region_zone'] = NOT_USED_ON_DESTROY

    ec_config = config.read_config_map()

    tf_data['billing_account'] = ec_config['billing_account']
    tb_discriminator = ec_config['tb_discriminator']
    tf_data['tb_discriminator'] = tb_discriminator

    env_data = None

    terraform_state_bucket = ec_config['terraform_state_bucket']
    # location of this solution's state with terraform bucket
    backend_prefix = get_solution_backend_prefix(solution_id, tb_discriminator)
    # source of the terraform used for this deployment
    terraform_source_path = '/app/terraform/solution_creation'

    tf = Terraform(working_dir=terraform_source_path, variables=tf_data)

    terraform_init(backend_prefix, terraform_state_bucket, tf)

    delete_workspace_repo(ec_config, tf)

    return terraform_destroy(env_data, tf)


def delete_workspace_repo(ec_config, tf):
    _, tf_state_json, _ = tf.show(json=True)
    tf_state: dict = json.loads(tf_state_json)
    if 'values' in tf_state:
        # only remove if state exists
        solution_name = tf_state['values']['outputs']['solution_folder']['value']['display_name']
        logger.debug("solution_name {}".format(solution_name))
        repo_name = "{}_workspace".format(solution_name)
        workspace_project_id = tf_state['values']['outputs']['workspace_project']['value']['project_id']
        logger.debug("workspace_project_id {}".format(workspace_project_id))
        eagle_project_id = ec_config['ec_project_name']
        logger.debug("eagle_project_id {}".format(eagle_project_id))
        delete_repo(repo_name, workspace_project_id, eagle_project_id)


def get_solution_backend_prefix(solution_id, tb_discriminator):
    return 'solution-' + str(solution_id) + '-' + tb_discriminator

def call_process(call_string):
    logger.debug("Process executed: {}".format(call_string))
    command_line_args = shlex.split(call_string)
    subprocess_call = subprocess.Popen(command_line_args, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT, universal_newlines=True)
    process_output, _ = subprocess_call.communicate()
    logger.debug("Process output: {}".format(process_output))


    