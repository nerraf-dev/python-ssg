import markdown, jinja2, toml, re

def load_config(config_string):
  return toml.loads(config_string)

def load_content_items(content_strings):
  items = []
  for item in content_strings:
    frontmatter, content = re.split("^\s*\+\+\+\+\+\s*$", item, 1, re.MULTILINE)
    item = toml.loads(frontmatter)
    item['content'] = markdown.markdown(content)
    items.append(item)

  # sort in reverse chron order
    items.sort(key=lambda x: x["data"],reverse=True)

    return items

def load_templates():
  pass

def render_site(config, content, templates):
  pass

def main():
  config_string = """
  title = "My Blog"
  """

  content_strings = ["""
                     title = "First Post
                     date = 2021-12-12T12:00:00+01:00
                     +++++

                     Hello! This is a **blog**
                     """,
                    """
                     title = "Post number two!"
                     date = 2021-12-24T12:03:56+01:00
                     +++++

                     Number two! <snigger>
                     """]
  
  config = load_config(config_string)
  content = load_content_items(content_strings)
  templates = load_templates()
  render_site(config, content, templates)

main()