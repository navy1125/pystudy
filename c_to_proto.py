#coding:utf-8
import sys
# reload(sys)
# sys.setdefaultencoding('UTF-8')
import os

import CppHeaderParser
from type_convert import c_to_proto_type

properties = "properties"

# 类型属性
protected = "protected"
public = "public"
private = "private"

# CppHeaderParser存储数据类型字段
RAW_TYPE = "raw_type"
# 变量变字段名
NAME = "name"

field_proper = {
    1:"optional",
    2:"required",
}

BASE_CLASS_NAME = "t_NullCmd"


def get_field_proper(ptype=1):
    return field_proper.get(ptype)


class CToProtoHandler(object):

    def __init__(self, file_name):
        self.file_name = file_name
        self.cppHeader = CppHeaderParser.CppHeader(file_name)

    def get_struct_name(self):
        #print "cppHeader.show =",self.cppHeader.show()
        return self.cppHeader.classes.keys()

    def get_define_name(self):
        return self.cppHeader.defines

    def get_enums(self):
        """
        {'line_number': 33, 'typedef': False, 'doxygen': '/**< \xd6\xd0\xc1\xa2\xc7\xf8id *//**< \xb8\xb1\xb1\xbe\xb9\xfa\xbc\xd2id *//**< \xc3\xbf\xb8\xf6\xc8\xcb\xd7\xd4\xbc\xba\xcb\xf9\xd4\xda\xb9\xfa\xa3\xac\xd2\xbb\xb0\xe3\xce\xaa\xc8\xba\xb7\xa2\xcf\xfb\xcf\xa2\xd3\xc3 */', 'name': 'CountryID', 'namespace': '', 'values': [{'name': 'CountryID_Middle', 'value': 13}, {'name': 'CountryID_Copy', 'value': 14}, {'name': 'CountryID_Self', 'value': 15}], 'type': <type 'int'>}, 
        """
        return self.cppHeader.enums

    def parser_properties(self, p_cls, n_index):
        """
        获得直接定义的属性
        params     c_cls        要获取的结构或类名,通过CppHeader.classes[xx]获取
        params     n_index      标签值,required int64 acctID = 1,1就是标签
        """
        ret_str = ""
        if properties in p_cls:
            properdata = p_cls[properties]
            for p_type, p_data in properdata.items():  # p_type = protected,public,private
                for variable_data in p_data:
                    variable_name = variable_data.get(NAME, "")
                    variable_type = variable_data.get(RAW_TYPE, "").lower()
                    type_str = ""
                    #是否是数组
                    if variable_data.has_key("array_size"):
                        array_size = int(variable_data.has_key("array_size"))
                        if array_size > 0:
                            type_str = "string"
                        else:
                            type_str = "bytes"
                    else:
                        type_str = c_to_proto_type.get(variable_type)
                    ret_str += "    %s %s %s = %s;\n" % (
                        get_field_proper(),type_str, variable_name, n_index)
                    n_index += 1
        return ret_str

    def parser_enums(self):
        ret_str = ""
        enums_list = self.get_enums()
        for enum in enums_list:
            #ret_str += "%s"%enum.get("doxygen")
            #print "enum = ",enum
            ret_str += "enum %s\n{\n"%enum.get("name")
            enum_data = enum.get("values")
            #print "enum_data = ",enum_data
            for enum_dic in enum_data:
                ret_str += "    %s    = %s;\n"%(enum_dic.get("name"),enum_dic.get("value"))
            ret_str += "} \n\n"
        return ret_str

    def get_method(self, p_cls):
        return p_cls.get("methods", "")

    def get_const_variable(self,p_cls):
        '''
        Function: get_const_variable
        Summary: 获得全局定义的一些变量
        Attributes: 
            @param (self):类实指针
            @param (p_cls):需要取变量的类
        Returns: List
        [{'raw_type': 'BYTE', 'line_number': 78, 'typedef': None, 'unresolved': True, 'constant': 1, 'name': 'LOGIN_SCENECMD', 'parent': None, 'default': '1', 'pointer': 0, 'defaultValue': '1', 'function_pointer': 0, 'static': 0, 'fundamental': 0, 'mutable': False, 'extern': False, 'typedefs': 0, 'array': 0, 'type': 'const BYTE', 'class': 0, 'reference': 0, 'aliases': ['BYTE']},]
        '''
        return p_cls.variables

    def parser_const_variable(self):
        #处理全局变量,并生成message结构体
        variable_list = self.get_const_variable(self.cppHeader)
        need_variable = ("LOGIN_SCENECMD","FORWARD_SCENECMD","MAP_SCENECMD")    #暂时手写后面需要再手动传入
        temlist = []
        for temdic in variable_list:
            if temdic.get("name") in need_variable:
                temlist.append(temdic);
        return temlist


    def parser2(self):
        ret_str = "package GameSmd;\n\n"#%self.file_name.split(".")[0]

        #获取enum
        ret_str += self.parser_enums()

        #解析基类
        all_struct_list = self.get_struct_name()
        #print "all_struct_list=",all_struct_list

        base_class_list = [];
        base_class_dict = {};  #{"stLoginSceneCmd":["stLoginLoginSceneCmd","stRefreshLoginSceneCmd"]}

        for struct_name in all_struct_list:
            cls_data = self.cppHeader.classes.get(struct_name,None)
            if cls_data is None:
                continue
            #print "aaa=",dir(cls_data)
            #print "aaa method =",cls_data["methods"]
            #print "name =",cls_data["name"]
            #print "aaa .show =",cls_data.show()
            #查找是否是需要提取的基类
            tmList1 = cls_data.get_all_methods()
            '''
            [{'line_number': 31, 'parent': {'inherits': [{'access': 'public', 'class': 't_NullCmd', 'virtual': False}], 
'line_number': 29, 'doxygen': '//////////////////////////////////////////////////////////////\n/// ???????????\xd6\xb8??//////////////////////////////////////////////////////////////', 'name': 'stLoginSceneCmd', 'parent': None, 'abstract': False, 'namespace': '', 'declaration_method': 'struct', 'properties': {'protected': [], 'public': [], 'private': []}, 'forward_declares': {'protected': [], 'public': [], 'private': []}, 'typedefs': {'protected': [], 'public': [], 'private': []}, 'structs': {'protected': [], 'public': [], 'private': []}, 'enums': {'protected': [], 'public': [], 'private': []}, 'final': False, 'nested_classes': [], 'methods': {'protected': [], 'public': [{...}], 'private': []}}, 'defined': True, 'namespace': '', 'operator': False, 'static': False, 'returns_fundamental': True, 'rtnType': 'void', 'extern': False, 'path': 'stLoginSceneCmd', 'returns_pointer': 0, 'parameters': [], 'class': None, 'returns_reference': False, 'const': False, 'name': 'stLoginSceneCmd', 'pure_virtual': False, 'debug': '\t stLoginSceneCmd ( ) \t {', 'explicit': False, 'virtual': False, 'destructor': False, 'returns': '', 'template': False, 'constructor': True, 'override': False, 'inline': False, 'final': False, 'friend': False, 'returns_class': False}]
            '''
            for temdic in tmList1:
                #print "temdic =",temdic
                parent = temdic.get("parent");
                if parent is None:
                    continue;
                inherits = parent.get("inherits");
                if inherits is None or len(inherits) <= 0:
                    continue;
                #print "inherits = ",inherits
                if inherits[0].get("class") == BASE_CLASS_NAME:
                    base_class_list.append(cls_data["name"])


        #print "list =",base_class_list

        for struct_name in all_struct_list:
            cls_data = self.cppHeader.classes.get(struct_name,None)
            if cls_data is None:
                continue;
            tmList1 = cls_data.get_all_methods()
            for temdic in tmList1:
                parent = temdic.get("parent");
                if parent is None:
                    continue;
                inherits = parent.get("inherits");
                if inherits is None or len(inherits) <= 0:
                    continue;
                if inherits[0].get("class") in base_class_list:
                    if base_class_dict.has_key(inherits[0].get("class")):
                        curlist = base_class_dict[inherits[0].get("class")]
                        if cls_data["name"] not in curlist:
                            curlist.append(cls_data["name"])
                        #base_class_dict[inherits[0].get("class")].append(cls_data["name"])
                    else:
                        base_class_dict[inherits[0].get("class")] = [cls_data["name"]]
        print "base_class_dict=",base_class_dict

        #处理最上面的消息头定义如:
        # message stLoginSceneCmd
        # {
        #     enum Param
        #     {
        #         stSetFilterCmdLoginSceneCmd = 1
        #         stLoginLoginSceneCmd = 2
        #         stStartGameLoginSceneCmd = 3
        #         stRefreshLoginSceneCmd = 4
        #         stSetPreCreateRoleLoginSceneCmd = 5
        #     }
        # }
        for k,v in base_class_dict.items():
            ret_str += "message %s\n{\n    enum Param\n    {\n"%(k)
            idx = 1
            for class_name in v:
                ret_str += "        %s = %s\n"%(class_name,idx)
                idx += 1;
            ret_str += "    }\n}\n\n"




        for k,v in base_class_dict.items():
            
            
            for class_name in v:
                nIndex = 1;
                ret_str += "message %s\n{\n"%class_name
                cls_data = self.cppHeader.classes.get(class_name,None)
                if cls_data is None:
                    continue;
                # properties = cls_data["properties"]
                # '''
                # properties数据如下
                # {'protected': [], 
                # 'public': [
                # {'raw_type': 'BYTE', 'line_number': 66, 'typedef': None, 'unresolved': True, 'constant': 0, 'name': 'cmd', 'parent': None, 'pointer': 0, 'namespace': '', 'function_pointer': 0, 'property_of_class': 'stSetFilterCmdLoginSceneCmd', 'static': 0, 'fundamental': 0, 'mutable': False, 'extern': False, 'typedefs': 0, 'array': 0, 'type': 'BYTE', 'class': 0, 'reference': 0, 'aliases': ['BYTE']}, 
                # 'private': []}
                # '''
                # #直接取public就可以了，因为是结构体都是public
                # public_data = properties["public"]
                # for proper in public_data:
                #     ret_str += "        %s %s %s = %s;\n"%(get_field_proper(),)
                # return;
                ret_str += self.parser_properties(cls_data,nIndex)
                nIndex += 1
                ret_str += "}\n\n"

        return ret_str

    def parser(self):

        ret_str = "package %s;\n\n"%self.file_name


        #获取enum
        ret_str += self.parser_enums()

        #解析基类
        all_struct_list = self.get_struct_name()
        print "all_struct_list = ",all_struct_list
        for struct_name in all_struct_list:
            cls_data = self.cppHeader.classes.get(struct_name, None)
            if cls_data is None:
                continue
            nindex = 1
            #ret_str += "%s\n"%cls_data.get("doxygen","").decode("utf8")
            ret_str += "message %s \n{\n" % struct_name
            method_info = self.get_method(cls_data)
            base_cls_list = set()
            # cppHeader如果在子类中初始化基类信息,获取不到相应的变量名,直接拿类名
            for method_key, method_lst in method_info.items():
                #method_key = public/protected/private
                for method_data in method_lst:
                    #'public': [{'line_number': 158,'parent': {'inherits': [{'access': 'public', 'class': 't_NullCmd', 'virtual': False}]
                    if method_data.get("parent"):
                        inherits = method_data.get("parent").get("inherits")
                        if len(inherits) > 0:
                            base_cls_name = inherits[0].get("class", None)
                            base_cls_list.add(base_cls_name)
        #解析基类名结束

            for cls_name in base_cls_list:
                ret_str += "    %s %s %s = %s;\n" % (
                    get_field_proper(), cls_name, cls_name.lower(), nindex)
                nindex += 1
            #print "properties =",self.parser_properties(cls_data,nindex)
            ret_str += self.parser_properties(cls_data,nindex)

            ret_str += "}\n\n"

        return ret_str


def parser_file(file_name):
    handle = CToProtoHandler(file_name)
    ret = handle.parser2();
    name_prefix = file_name.split(".")[0]
    tartget_name = "%s.proto"%name_prefix
    with open(tartget_name,"w") as f:
        f.write(ret)
    #print ret


if __name__ == "__main__":
    file_list = os.listdir(os.getcwd())
    #file_list = ["GameInCommand.h"]
    for file_name in file_list:
        tm_list = os.path.splitext(file_name)
        if tm_list[1] == ".h":
            print "file_name =",file_name
            try:
                parser_file(file_name)
            except Exception as e:
                print "err=",e

        
