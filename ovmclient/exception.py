# Copyright (c) 2017 Cloudbase Solutions Srl
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class OVMClientException(Exception):
    pass


class ObjectNotFoundException(OVMClientException):
    pass


class TooManyObjectsException(OVMClientException):
    pass


class OVMClientRequestException(OVMClientException):
    def __init__(self, error_data, http_status_code):
        super(OVMClientRequestException, self).__init__(
            str({"error_data": error_data,
                 "http_status_code": http_status_code}))
        self.error_data = error_data
        self.http_status_code = http_status_code


class JobFailureException(OVMClientException):
    def __init__(self, job):
        super(JobFailureException, self).__init__(
            "Job failed: %s" % job["error"])
        self.job = job
