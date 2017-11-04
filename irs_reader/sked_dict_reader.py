from .type_utils import dictType, orderedDictType, listType, \
    unicodeType, noneType, strType
from .flatten_utils import flatten
from .keyerror_utils import ignorable_keyerror
from .settings import LOG_KEY


class SkedDictReader(object):
    """
    We get an ordered dict back from xmltodict, but we want to "flatten" it
    into xpath-ed variables and repeated structures.
    Will also work on reading xmltodict that was previously turned into json
    """
    def __init__(
        self,
        standardizer,
        groups,
        object_id,
        ein,
        documentId=None,
        documentation=False,
        csv_format=False
    ):

        self.standardizer = standardizer
        self.object_id = object_id
        self.ein = ein
        self.documentId = documentId
        self.schedule_parts = {}         # allows one entry per filing
        self.repeating_groups = {}       # multiple per filing
        self.csv_format = csv_format     # Do we need to generate ordered csv
        self.for_csv_list = []           # keep record of elements, line by line
        self.groups = groups
        self.documentation = documentation
        self.variable_keyerrors = []    # record any unexpected variables
        self.group_keyerrors = []       # or unexpected groups

        if self.documentation and not self.standardizer.get_documentation_status():
            # Todo: split out documenter entirely so we don't have to do this
            raise Exception(
                "Standardizer must be initialized with the \
                documentation flag to load documentation"
            )

    def _get_table_start(self):
        """ prefill the columns we need for all tables """
        if self.documentation:
            standardized_table_start = {
                'object_id': {
                    'value': self.object_id,
                    'ordering': -1,
                    'line_number': 'NA',
                    'description': 'IRS-assigned object id',
                    'db_type': 'String(18)'
                },
                'ein': {
                    'value': self.ein,
                    'ordering': -2,
                    'line_number': 'NA',
                    'description': 'IRS employer id number',
                    'db_type': 'String(9)'
                }
            }
            if self.documentId:
                standardized_table_start['documentId'] = {
                    'value': self.documentId,
                    'description': 'Document ID',
                    'ordering': 0
                }
        else:
            standardized_table_start = {
                'object_id': self.object_id,
                'ein': self.ein
            }
            if self.documentId:
                standardized_table_start['documentId'] = self.documentId

        return standardized_table_start

    def _process_group(self, json_node, path, this_group):

        for node_index, node in enumerate(json_node):
            #print("_process_group %s " % (this_group['db_name']))
            this_node_type = type(node)
            flattened_list_item = None
            if this_node_type == unicodeType:
                #print("_pg: unicodeType %s ")
                flattened_list_item = {path: node}
            else:
                #print("_pg: NOT unicodeType")
                flattened_list_item = flatten(node, parent_key=path, sep='/')
            table_name = None
            standardized_group_dict = self._get_table_start()

            for xpath in flattened_list_item.keys():
                if '@' in xpath:
                    continue
                else:
                    xpath = xpath.replace("/#text", "")
                    value = flattened_list_item[xpath]

                    if self.csv_format:
                        this_var = {
                            'xpath':xpath,
                            'value':value,
                            'in_group':True,
                            'group_name':this_group['db_name'],
                            'group_index':node_index
                        }
                        self.for_csv_list.append(this_var)

                    try:
                        this_var_data = self.standardizer.get_var(xpath)
                    except KeyError:
                        if not ignorable_keyerror(xpath):
                            self.variable_keyerrors.append(
                                {'element_path':xpath}
                            )
                        continue
                    this_var_value = flattened_list_item[xpath]
                    this_var_name = this_var_data['db_name']
                    table_name = this_var_data['db_table']
                    if self.documentation:
                        result = {
                            'value': this_var_value,
                            'ordering': this_var_data['ordering'],
                            'line_number': this_var_data['line_number'],
                            'description': this_var_data['description'],
                            'db_type': this_var_data['db_type']
                        }
                        standardized_group_dict[this_var_name] = result

                    else:
                        standardized_group_dict[this_var_name] = this_var_value
            try:
                self.repeating_groups[table_name].append(standardized_group_dict)
            except KeyError:
                self.repeating_groups[table_name] = [standardized_group_dict]

    def _parse_json(self, json_node, parent_path=""):
        this_node_type = type(json_node)
        element_path = parent_path

        if this_node_type == listType:
            #print("List type %s" % element_path)

            this_group = None
            try:
                this_group = self.groups[element_path]
            except KeyError:
                self.group_keyerrors.append(
                    {'element_path':element_path}
                )
            self._process_group(json_node, parent_path, this_group)

        elif this_node_type == unicodeType:
            # but ignore it if is an @.
            if '@' in element_path:
                pass
            else:
                element_path = element_path.replace("/#text", "")
                try:
                    # is it a group?
                    this_group = self.groups[element_path]
                    self._process_group(
                        [{parent_path: json_node}],
                        '',
                        this_group
                    )

                except KeyError:

                    # It's not a group so it should be a variable we know about
                    
                    if self.csv_format:
                        this_var = {
                            'xpath':element_path,
                            'value':json_node,
                            'in_group':False,
                            'group_name':None,
                            'group_index':None
                        }
                        self.for_csv_list.append(this_var)

                    # It's not a group so it should be a variable we know about
                    try:
                        var_data = self.standardizer.get_var(element_path)
                        var_found = True

                    except KeyError:
                        # pass through for some common key errors
                        # [ TODO: FIX THE KEYERRORS! ]
                        if not ignorable_keyerror(element_path):
                            self.variable_keyerrors.append(
                                {'element_path':element_path}
                            )
                        var_found = False

                    if var_found:

                        table_name = var_data['db_table']
                        var_name = var_data['db_name']

                        result = json_node
                        if self.documentation:
                            result = {
                                'value': json_node,
                                'ordering': var_data['ordering'],
                                'line_number': var_data['line_number'],
                                'description': var_data['description'],
                                'db_type': var_data['db_type']
                            }

                        try:
                            self.schedule_parts[table_name][var_name] = result
                        except KeyError:
                            self.schedule_parts[table_name] = self._get_table_start()
                            self.schedule_parts[table_name][var_name] = result


        elif this_node_type == orderedDictType or this_node_type == dictType:

            try:
                # is it a singleton group?
                this_group = self.groups[element_path]
                self._process_group([{parent_path: json_node}], '', this_group)

            except KeyError:
                keys = json_node.keys()
                for key in keys:
                    new_path = parent_path + "/" + key
                    self._parse_json(json_node[key], parent_path=new_path)

        elif this_node_type == noneType:
            pass

        elif this_node_type == strType:
            msg = "String '%s'" % json_node
            #self.logging.debug(msg)
        else:
            raise Exception("Unhandled type: %s" % (type(json_node)))

    def parse(self, raw_ordered_dict, parent_path=""):
        self._parse_json(raw_ordered_dict, parent_path=parent_path)
        return ({
            'schedule_parts': self.schedule_parts,
            'groups': self.repeating_groups,
            'csv_line_array':self.for_csv_list,    # This is empty if not csv
            'keyerrors':self.variable_keyerrors,
            'group_keyerrors':self.group_keyerrors
        })
