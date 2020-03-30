#!/usr/bin/env python

import yaml
import json
import re
from collections import OrderedDict

camelcase_regex = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')

def camelcase_to_snakecase(s):
    s = s.replace('GameCenter', 'Gamecenter')
    return camelcase_regex.sub(r'_\1', s).lower()

def process_arguments(func):
    param_map = {}
    if func['swagger'].has_key('parameters'):
        for param in func['swagger']['parameters']:
            param_map[param['name']] = param

    func['has_query_arguments'] = False
    func['has_body_arguments'] = False
    for arg_name, arg_def in func['arguments'].items():
        if not arg_def.has_key('required'):
            arg_def['required'] = False
        if func['url'].find('{%s}' % arg_name) != -1:
            arg_def['in'] = 'path'
        elif param_map.has_key(arg_name):
            arg_def['in'] = param_map[arg_name]['in']
            func['has_query_arguments'] = True
        else:
            arg_def['in'] = 'body'
            func['has_body_arguments'] = True

def get_funcs_from_definition(swagger, method_definitions):
    funcs = {}

    for url, methods in swagger['paths'].items():
        for method, definition in methods.items():
            name = camelcase_to_snakecase(definition['operationId'])
            if not method_definitions.has_key(name):
                #print("Missing method definition for: %s" % name)
                continue
            func = {
                'name': name,
                'comment': definition.get('summary'),
                'url': url,
                'method': method,
                'arguments': method_definitions[name],
                'swagger': definition,
            }
            process_arguments(func)
            funcs[name] = func
    return funcs

def generate_default(default):
    if default is False:
        return 'false'
    elif default is True:
        return 'true'
    elif isinstance(default, basestring):
        return "'" + default + "'"
    elif isinstance(default, list):
        l = []
        for x in default:
            l.append(generate_default(x))
        return '[' + ', '.join(l) + ']'
    elif isinstance(default, dict):
        return '{}'
    else:
        return str(default)

def generate_method(method):
    return 'HTTPClient.METHOD_' + method.upper()

def generate_path(url, args):
    url = '\'%s\'' % url.lstrip('/')
    for arg_name, arg_def in args.items():
        url = url.replace('{%s}' % arg_name, '\' + %s + \'' % arg_name)
    url = url.replace(' + \'\'', '')
    return url

def generate_func(func):
    args = []
    args_def_map = {}

    for arg_name, arg_def in func['arguments'].items():
        arg = arg_name + ': ' + arg_def['type']
        if arg_def.has_key('default'):
            args_def_map[arg_name] = generate_default(arg_def['default'])
            arg += ' = ' + args_def_map[arg_name]
        args.append(arg)

    output  = 'signal %s_completed (response, request)\n\n' % func['name']
    output += '# ' + func['comment'] + '\n'
    output += 'func %s(%s):\n' % (func['name'], ', '.join(args))
    output += '\tvar request = {\n'
    output += '\t\tmethod = ' + generate_method(func['method']) + ',\n'
    output += '\t\tpath = ' + generate_path(func['url'], func['arguments']) + ',\n'
    if func['has_body_arguments']:
        output += '\t\tdata = {},\n'
    if func['has_query_arguments']:
        output += '\t\tquery_string = {},\n'
    output += '\t\tname = \'%s\',\n' % func['name']
    output += '\t}\n'
    output += '\t\n'

    has_any_args = False
    for arg_name, arg_def in func['arguments'].items():
        if arg_def['in'] == 'path':
            continue
        has_any_args = True

        part = 'query_string' if arg_def['in'] == 'query' else 'data'

        arg_value = arg_name

        if arg_name == 'data':
            output += '\trequest[\'data\'] = %s\n' % arg_value
        elif args_def_map.has_key(arg_name) and not arg_def['required']:
            output += '\tif %s != %s:\n' % (arg_name, args_def_map[arg_name])
            output += '\t\trequest[\'%s\'][\'%s\'] = %s\n' % (part, arg_name, arg_value)
        else:
            output += '\trequest[\'%s\'][\'%s\'] = %s\n' % (part, arg_name, arg_value)

    if has_any_args:
        output += '\t\n'

    output += '\treturn _queue_request(request)\n'
    
    return output

def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass
    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))
    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

def main():
    with open('nakama.swagger.json') as fd:
        swagger = json.load(fd)
    with open('method_definitions.yml') as fd:
        method_definitions = ordered_load(fd, yaml.SafeLoader)
    funcs = get_funcs_from_definition(swagger, method_definitions)

    output = []
    for name in method_definitions.keys():
        func = funcs[name]
        output.append(generate_func(func))

    print '#'
    print '# AUTOMATICALLY GENERATED:'
    print '#'
    print ''

    print '\n'.join(output) + '\n'

if __name__ == '__main__': main()

