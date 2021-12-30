import markdown, jinja2, toml, re
import os, glob, pathlib, shutil, distutils.dir_util

'''
load_config: gets blog base configuration from .toml file
'''
def load_config(config_filename):
  with open(config_filename, 'r') as config_file:
    return toml.loads(config_file.read())

'''
load_content_items: open and read file containing page content
'''
def load_content_items(content_directory):
  items = []
  for fn in glob.glob(f"{content_directory}/*.md"):
    with open(fn, 'r') as file:
      frontmatter, content = re.split("^\s*\+\+\+\+\+\s*$", file.read(), 1, re.MULTILINE)
    item = toml.loads(frontmatter)
    item['content'] = markdown.markdown(content)
    item['slug'] = os.path.splitext(os.path.basename(file.name))[0]
    item['url'] = f"/{item['date'].year}/{item['date'].month:0>2}/{item['slug']}/"
    
    items.append(item)

  # sort in reverse chron order
  items.sort(key=lambda x: x["date"],reverse=True)
  return items

def load_templates(template_directory):
  file_system_loader = jinja2.FileSystemLoader(template_directory)
  return jinja2.Environment(loader = file_system_loader)

def render_site(config, content, environment, output_directory):
  if os.path.exists(output_directory):
    shutil.rmtree(output_directory)
  os.mkdir(output_directory)

  #Homepage
  index_template = environment.get_template("index.html")
  with open(f"{output_directory}/index.html",'w') as file:
    file.write(index_template.render(config = config, content = content))

  #Post pages
  post_template = environment.get_template("post.html")
  for item in content["posts"]:
    path = f"{output_directory}/{item['url']}"
    pathlib.Path(path).mkdir(parents=True, exist_ok = True)
    with open(path+"index.html",'w') as file:
      file.write(post_template.render(this = item, config = config, content = content))

  #Static files
  distutils.dir_util.copy_tree("static", "public")

def main():
 
  config = load_config("config.toml")
  content = { "posts": load_content_items("content/posts") }
  environment = load_templates("layout")
  render_site(config, content, environment, "public")

main()