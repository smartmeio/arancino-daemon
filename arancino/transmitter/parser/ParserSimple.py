# coding=utf-8
"""
SPDX-license-identifier: Apache-2.0

Copyright (c) 2021 smartme.IO

Authors:  Sergio Tomasello <sergio@smartme.io>

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License
"""

from arancino.transmitter.parser.Parser import Parser
from arancino.utils.ArancinoUtils import ArancinoLogger, ArancinoConfig
import arancino.ArancinoConstants as CONST


LOG = ArancinoLogger.Instance().getLogger()
CONF = ArancinoConfig.Instance()
TRACE = CONF.get_log_print_stack_trace()



class ParserSimple(Parser):

    def __init__(self, cfg=None):
        super().__init__(cfg=cfg)

    def start(self):
        pass

    def stop(self):
        pass

    def _do_elaboration(self, data=None):
        LOG.debug("{}Parsing Data...".format(self._log_prefix))
        metadata = []
        rendered_data = []
        try:

            # do parsing only if data contains data
            if data or len(data) > 0:

                # do parsing only if template is loaded
                if self._tmpl:
                    for d in data:
                        last_tms = int(self._datastore_tser.redis.get("{}:{}:{}".format(d["key"], self._flow_name, CONST.SUFFIX_TMSTP)))
                        for i in range(len(d["timestamps"])):
                            if d["timestamps"][0] > last_tms:
                                break
                            else:
                                del d["timestamps"][0]
                                del d["values"][0]

                        if not len(d["values"]):
                            continue
                        
                        md = {}
                        md["key"] = d["key"]
                        md["flow_name"] = self._flow_name
                        md["last_ts"] = max(d["timestamps"])
                        metadata.append(md)

                        rd = self._tmpl.render(data=d)
                        rendered_data.append(rd)

                    LOG.debug("{}Parsed data: {}".format(self._log_prefix, rendered_data))
                    return rendered_data, metadata
                else:
                    LOG.warning("{}No template to be parsed.".format(self._log_prefix))
                    return None, None

            else:
                LOG.warning("{}No data to parse.".format(self._log_prefix))
                return None, None

        except Exception as ex:
            LOG.error("{}Parsing Error: {}".format(self._log_prefix, ex), exc_info=TRACE)
            return None, None


