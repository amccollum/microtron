import isodate, re
import lxml.etree, lxml.html

class ParseError(Exception):
    pass

class Parser(object):
    def __init__(self, tree, formats, strict=False):
        self.root = tree
        self.formats = formats
        self.strict = strict
    
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
                    values.append((value, node.attrib['href'], node.text))

        return results
        
    def _parse_node(self, node, format, nested=[]):
        result = {}
        for prop in format:
            prop_name = prop.tag
            prop_type = prop.attrib['type'] if 'type' in prop.attrib else None
            prop_mandatory = True if 'mandatory' in prop.attrib and prop.attrib['mandatory'] == 'yes' else False
            prop_many = prop.attrib['many'] if 'many' in prop.attrib else False
            prop_couldbe = set(prop.attrib['couldbe'].split('|')) if 'couldbe' in prop.attrib else []
            prop_values = set(prop.attrib['values'].split(',')) if 'values' in prop.attrib else None

            # Select all properties, but exclude nested properties
            prop_expr = 'descendant-or-self::*[contains(concat(" ", normalize-space(@class), " "), " %s ")]' % prop_name
            parent_expr = 'ancestor::*[contains(concat(" ", normalize-space(@class), " "), " %s ")]' % format.tag
            prop_nodes = [prop_node for prop_node in node.xpath(prop_expr) if prop_node.xpath(parent_expr)[0] == node]
    
            if self.strict and not prop_nodes and prop_mandatory:
                raise ParseError("Missing mandatory property: %s" % (prop_name))

            if prop_many == 'many':
                values = []
            elif prop_many == "manyasone":
                values = ""

            for prop_node in prop_nodes:
                try:
                    for mf in prop_couldbe:
                        try:
                            value = self.parse(mf, prop_node)[0]
                            if value:
                                break
                        except:
                            pass
                        
                    else:
                        if len(prop):
                            value = self._parse_node(prop_node, prop)
                            if not value:
                                value = self._parse_value(prop_node)
                     
                        elif not prop_type or prop_type in ('text', 'url', 'image'):
                            value = self._parse_value(prop_node)
            
                        elif prop_type == 'date':
                            value = isodate.parse_date(self._parse_value(prop_node))
                    
                        else:
                            value = self.parse_format(prop_type, prop_node)[0]
                            if not value:
                                value = self._parse_value(prop_node)
                
                except Exception, e:
                    if self.strict:
                        raise ParseError("Error parsing value for property %s: %s" % (prop_name, e))
                    else:
                        value = self._parse_value(prop_node)
            
                if self.strict and prop_values and value.lower() not in prop_values:
                    raise ParseError("Invalid value for property %s: %s" % (prop_name, value))
            
                if prop_many == 'many':
                    values.append(value)
                elif prop_many == 'manyasone':
                    values += value
                else:
                    result[prop_name] = value
                    break
            
            if prop_many and values:
                result[prop_name] = values
            
        return result
        
    def _parse_value(self, node):
        value_expr = 'descendant::*[contains(concat(" ", normalize-space(@class), " "), " value ")]'
        value_nodes = node.xpath(value_expr)

        if value_nodes:
            return self._normalize_space(" ".join(value_node.text_content() for value_node in value_nodes))
            
        elif node.tag == 'abbr' and 'title' in node.attrib:
            return node.attrib['title']
        
        elif 'href' in node.attrib:
            href = node.attrib['href']
            for prefix in ('mailto:', 'tel:', 'fax:', 'modem:'):
                if href.startswith(prefix):
                    href = href[len(prefix):]
                    break
            
            return (href, self._normalize_space(node.text_content()))
            
        elif 'src' in node.attrib:
            return node.attrib['src']
        
        else:
            return self._normalize_space(node.text_content())
    
    def _normalize_space(self, text):
        return re.sub(r'\s+', ' ', text.strip())


if __name__ == "__main__":
    import pprint, sys
    tree = lxml.html.parse(sys.argv[1])
    formats = lxml.etree.parse(sys.argv[2])
    
    pprint.pprint(Parser(tree, formats).parse_format(sys.argv[3]))
