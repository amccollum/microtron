__import__('pkg_resources').declare_namespace(__name__)

import isodate, re, os
import lxml.etree


class ParseError(Exception):
    def __init__(self, message, sourceline=None):
        Exception.__init__(self, message)
        self.sourceline = sourceline

class Parser(object):
    def __init__(self, tree, formats=None, strict=False, collect_errors=False):
        # if collect_errors is True, exceptions will be trapped and
        # accumulated in self.errors
        self.root = tree
        self.formats = formats
        self.strict = strict
        self.collect_errors = collect_errors
        self.errors = []
        if not formats:
            path = os.path.abspath(os.path.dirname(__file__))
            fname = os.path.join(path, 'mf.xml')
            self.formats = lxml.etree.parse(fname)

    def parse_format(self, mf, root=None):
        root = root if root is not None else self.root
        format = self.formats.xpath('/microformats/*[@name="%s"] | /microformats/%s' % (mf, mf))
        if not format:
            return None
        else:
            format = format[0]

        results = []
        if format.attrib['type'] == 'compound':
            expr = 'descendant-or-self::*[contains(concat(" ", normalize-space(@class), " "), " %s ")]' % format.tag
            for node in root.xpath(expr):
                results.append(self._parse_node(node, format))

        elif format.attrib['type'] == 'elemental':
            for feature in format:
                attribute = feature.attrib['attribute']
                value = feature.tag
                expr = 'descendant-or-self::*[contains(concat(" ", normalize-space(@%s), " "), " %s ")]' % (attribute, value)

                for node in root.xpath(expr):
                    results.append({'__type__': mf, 'value': value, 'href': node.attrib['href'], 'text': node.text})

        return results

    def _parse_node(self, node, format):
        result = {'__type__': format.tag}
        for prop in format:
            prop_name = prop.tag
            prop_type = prop.attrib['type'] if 'type' in prop.attrib else None
            prop_mandatory = True if 'mandatory' in prop.attrib and prop.attrib['mandatory'] == 'yes' else False
            prop_attr = prop.attrib['attribute'] if 'attribute' in prop.attrib else 'class'
            prop_many = prop.attrib['many'] if 'many' in prop.attrib else False
            prop_couldbe = prop.attrib['couldbe'].split('|') if 'couldbe' in prop.attrib else []
            prop_values = set(prop.attrib['values'].split(',')) if 'values' in prop.attrib else None
            prop_separator = prop.attrib['separator'] if 'separator' in prop.attrib else ""
            
            # Select all properties, but exclude nested properties
            prop_expr = 'descendant-or-self::*[contains(concat(" ", normalize-space(@%s), " "), " %s ")]' % (prop_attr, prop_name)
            parent_expr = 'ancestor::*[contains(concat(" ", normalize-space(@class), " "), " %s ")]' % format.tag
            prop_nodes = [prop_node for prop_node in node.xpath(prop_expr) if prop_node.xpath(parent_expr)[0] == node]

            # missing something required?
            if self.strict and not prop_nodes and prop_mandatory:
                err = ParseError("missing mandatory %s property: %s" % (format.tag, prop_name), node.sourceline)
                if self.collect_errors:
                    self.errors.append(err)
                    continue
                else:
                    raise err

            if prop_many == 'many':
                values = []
            elif prop_many == 'manyasone':
                values = ""

            # for each node matching the property we're looking for...
            for prop_node in prop_nodes:
                try:
                    # Check if this prop_node is one or more of the possible "could be" formats
                    value = {}
                    for mf in prop_couldbe:
                        try:
                            format_results = self.parse_format(mf, prop_node)
                            if format_results and len(format_results[0]) > 1:
                                if '__type__' in value:
                                    value['__type__'] += ' ' + format_results[0].pop('__type__')

                                value.update(format_results[0])

                        except:
                            pass

                    # Check if this property is a compound property
                    if len(prop):
                        try:
                            prop_result = self._parse_node(prop_node, prop)
                            if len(prop_result) > 1:
                                if '__type__' in value:
                                    value['__type__'] += ' ' + prop_result.pop('__type__')

                                value.update(prop_result)
                        except:
                            pass

                    if not value:
                        value['__type__'] = prop_type
                        value['__srcline__'] = prop_node.sourceline
                        if not prop_type or prop_type == 'text':
                            value = self._parse_value(prop_node)

                        elif prop_type in ('url', 'email'):
                            value['text'] = self._parse_text(prop_node)
                            if 'href' in prop_node.attrib:
                                value['href'] = prop_node.attrib['href']
                                for prefix in ('mailto', 'tel', 'fax', 'modem'):
                                    if value['href'].lower().startswith(prefix + ':'):
                                        value[prefix] = value['href'][len(prefix + ':'):]
                                        break

                        elif prop_type == 'image':
                            if 'title' in prop_node.attrib:
                                value['title'] = prop_node.attrib['title']

                            if 'alt' in prop_node.attrib:
                                value['alt'] = prop_node.attrib['alt']

                            if 'src' in prop_node.attrib:
                                value['src'] = prop_node.attrib['src']

                        elif prop_type == 'object':
                            value['text'] = self._parse_text(prop_node)
                            if 'data' in prop_node.attrib:
                                value['data'] = prop_node.attrib['data']

                        elif prop_type == 'date':
                            value['text'] = self._parse_text(prop_node)
                            value['date'] = isodate.parse_date(self._parse_value(prop_node))

                        elif prop_type == 'datetime':
                            value['text'] = self._parse_text(prop_node)
                            value['datetime'] = isodate.parse_datetime(self._parse_value(prop_node))

                        else:
                            # Try to parse this property as a sub-format
                            results = self.parse_format(prop_type, prop_node)
                            if results and len(results[0]) > 1:
                                value = results[0]
                            else:
                                raise Exception("Could not parse expected format: '%s'" % (prop_type,))

                except Exception, e:
                    if self.strict:
                        err = ParseError("Error parsing value for property '%s': %s" % (prop_name, e), sourceline=prop_node.sourceline)
                        if self.collect_errors:
                            self.errors.append(err)
                            continue    # go on to next property
                        else:
                            raise err
                    else:
                        value = self._parse_value(prop_node)

                # Convert the value to a string (if it isn't one already)
                if isinstance(value, basestring):
                    value_text = value
                elif 'text' in value:
                    value_text = value['text']
                else:
                    value_text = ""

                if self.strict and prop_values and value_text.lower() not in prop_values:
                    err = ParseError("Invalid value for property '%s': %s" % (prop_name, value))
                    if self.collect_errors:
                        self.errors.append(err)
                        continue    # go on to next property
                    else:
                        raise err

                if prop_many == 'many':
                    values.append(value)

                elif prop_many == 'manyasone':
                    if value_text:
                        if values and prop_separator:
                            values += prop_separator

                        values += value_text

                else:
                    result[prop_name] = value
                    break

            if prop_many and values:
                result[prop_name] = values

        return result

    def _parse_value(self, node):
        value_expr = 'descendant::*[contains(concat(" ", normalize-space(@class), " "), " value ")]'
        value_nodes = node.xpath(value_expr)

        # Check for various methods to override the tag text
        if value_nodes:
            return " ".join(self._parse_text(value_node) for value_node in value_nodes)

        elif node.tag == 'abbr' and 'title' in node.attrib:
            return node.attrib['title']

        else:
            return self._parse_text(node)

    def _parse_text(self, node):
        text_expr = 'normalize-space(string(.))'
        return node.xpath(text_expr)
