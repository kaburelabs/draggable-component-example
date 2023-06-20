import inspect
from html.parser import HTMLParser
from dash import dcc, html


class DashHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._stack = []
        self.dash_object = None

    @staticmethod
    def get_dash_tag_class(tag):
        tag_title = tag.title()
        if not hasattr(html, tag_title):
            raise ValueError(f'Can not find Dash HTML tag {tag_title}')

        return getattr(html, tag_title)

    def handle_starttag(self, tag, attrs):
        dash_tag_class = self.get_dash_tag_class(tag)

        # Convert Attributes to Dash Attributes
        dash_attrs = {}
        if attrs:
            named_dash_attrs = list(inspect.signature(dash_tag_class.__init__).parameters)[1:-1]
            lower_named_dash_attrs = {n.lower(): n for n in named_dash_attrs}
            for attr_name, attr_value in attrs:
                lower_attr_name = attr_name.lower()
                if lower_attr_name == 'class':
                    dash_attrs['className'] = attr_value
                elif lower_attr_name == 'style':
                    style_dict = {}
                    for style in attr_value.split(';'):
                        style_key, style_value = style.split(':')
                        style_dict[style_key] = style_value
                    dash_attrs['style'] = style_dict
                elif lower_attr_name in ('n_clicks', 'n_clicks_timestamp'):
                    dash_attrs[lower_attr_name] = int(attr_value)
                elif lower_attr_name in lower_named_dash_attrs:
                    dash_attrs[lower_named_dash_attrs[lower_attr_name]] = attr_value
                else:
                    dash_attrs[attr_name] = attr_value
        
        # Create the real tag
        dash_tag = dash_tag_class(**dash_attrs)
        self._stack.append(dash_tag)

    def handle_endtag(self, tag):
        dash_tag_class = self.get_dash_tag_class(tag)
        dash_tag = self._stack.pop()
        if type(dash_tag) is not dash_tag_class:
            raise ValueError(f'Malformed HTML')

        # Final Tag
        if not self._stack:
            self.dash_object = dash_tag
            return

        # Set Children to always be a list
        if type(self._stack[-1].children) is not list:
            self._stack[-1].children = []

        # Append tag on to parent tag
        self._stack[-1].children.append(dash_tag)

    def handle_data(self, data):
        # Set Children to always be a list
        if type(self._stack[-1].children) is not list:
            self._stack[-1].children = []

        # Append tag on to parent tag
        self._stack[-1].children.append(data)


def html_to_dash(html_string):
    parser = DashHTMLParser()
    
    parser.feed(html_string)

    return parser.dash_object







