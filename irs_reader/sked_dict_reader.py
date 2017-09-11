import logging

from .type_utils import dictType, orderedDictType, listType, unicodeType, noneType, strType
from .flatten_utils import flatten
from .keyerror_utils import ignorable_keyerror
from .settings import LOG_KEY

class SkedDictReader(object):
    """
    We get an ordered dict back from xmltodict, but we want to "flatten" it
    into xpath-ed variables and repeated structures. 
    """
    def __init__(self, standardizer, groups, object_id, ein, documentId=None):

        self.standardizer = standardizer
        self.object_id = object_id
        self.ein = ein
        self.documentId=documentId
        self.schedule_parts = {} # allows one entry per filing
        self.repeating_groups = {} # multiple per filing
        self.groups = groups
        self.logging = logging.getLogger(LOG_KEY)


    def _get_table_start(self):
        """ prefill the columns we need for all tables """ 

        standardized_table_start = {'object_id':self.object_id, 'ein':self.ein}
        if self.documentId:
            standardized_table_start['documentId'] = self.documentId
        return standardized_table_start

    def _process_group(self, json_node, path, this_group):
        for node in json_node:
            this_node_type = type(node)
            flattened_list_item = None
            if this_node_type == unicodeType:
                flattened_list_item = {path:json_node}            
            else: # do we need to be picky about types? 
                flattened_list_item = flatten(node, parent_key=path, sep='/')
            table_name = None
            standardized_group_dict = self._get_table_start()

            for xpath in flattened_list_item.keys():
                if '@' in xpath or '#' in xpath:
                    continue
                else:
                    try:
                        this_var_data = self.standardizer.get_var(xpath)
                    except KeyError:
                        if not ignorable_keyerror(xpath):
                            msg = "Key error %s in %s ein=%s" % (xpath, self.object_id, self.ein)
                            self.logging.warning(msg)
                        continue
                    this_var_value = flattened_list_item[xpath]
                    this_var_name = this_var_data['db_name']
                    table_name = this_var_data['db_table']
                    standardized_group_dict[this_var_name] =  this_var_value 
            try:
                self.repeating_groups[table_name].append(standardized_group_dict) 
            except KeyError:
                self.repeating_groups[table_name] = [standardized_group_dict]

    def _parse_json(self, json_node, parent_path=""):
        this_node_type = type(json_node)
        element_path = parent_path # we've arrived
        if this_node_type == unicodeType:
            # but ignore it if is an @ or # - we get docId elsewhere
            if '@' in element_path or '#' in element_path:
                pass
            else:
                try:
                    # is it a group? 
                    this_group = self.groups[element_path]
                    self._process_group([{parent_path:json_node}], '', this_group)

                except KeyError:
                    # It's not a group so it should be a variable we know about

                        try:
                            var_data = self.standardizer.get_var(element_path)
                            var_found = True

                        except KeyError:
                            # pass through for some common key errors:
                            if not ignorable_keyerror(element_path):
                                msg = "Key error %s in %s ein=%s" % (element_path, self.object_id, self.ein)
                                self.logging.warning(msg)
                            var_found = False

                        if var_found:

                            table_name = var_data['db_table']
                            var_name = var_data['db_name']
                            try:
                                # Do we need the ordering downstream? Add --doc option to show line numbers, order vars
                                # this_sked = self.schedule_parts[table_name][var_name] = {'value': json_node, 'ordering': var_data['ordering'] }
                                # but if not:
                                self.schedule_parts[table_name][var_name] =  json_node    
                            except KeyError:
                                # ditto as above
                                self.schedule_parts[table_name] = self._get_table_start()
                                self.schedule_parts[table_name][var_name] = json_node 

        elif this_node_type == listType:

            this_group = None
            process_normal = True
            try:
                this_group = self.groups[element_path]
                
            except KeyError:                
                ## TODO: If this is multiple schedule k's, handle differently.
                msg = "Group error %s in %s ein=%s" % (element_path, self.object_id, self.ein)
                self.logging.warning(msg)
                process_normal = False
            self._process_group(json_node, parent_path, this_group)

        elif this_node_type == orderedDictType:
            keys = json_node.keys()
            for key in keys:
                new_path = parent_path + "/" + key
                self._parse_json(json_node[key], parent_path=new_path)

        elif this_node_type == noneType:
            pass
        
        elif this_node_type == strType:
            msg = "String '%s'" % json_node
            self.logging.debug(msg)
        else:
            raise Exception ("Unhandled type: %s" % (type(json_node)))

    def parse(self, raw_ordered_dict, parent_path=""):
        self._parse_json(raw_ordered_dict, parent_path=parent_path)
        return ({'schedule_parts': self.schedule_parts, 'groups': self.repeating_groups } )

