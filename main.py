import markdown, jinja2, toml, re
import os, glob, pathlib, shutil, distutils.dir_util
import inflect

'''
load_config: gets blog base configuration from .toml file
'''
def load_config(config_filename):
  with open(config_filename, 'r') as config_file:
    config = toml.loads(config_file.read())
    
  ie = inflect.engine()
  for content_type in config["types"]:
    config[content_type]["plural"] = ie.plural(content_type)
    
  return config

'''
load_content_items: open and read file containing page content
'''
def load_content_items(config, content_directory):
  def load_content_type(content_type):
    items = []
    for fn in glob.glob(f"{content_directory}/{config[content_type]['plural']}/*.md"):
      with open(fn, 'r') as file:
        frontmatter, content = re.split("^\s*\+\+\+\+\+\s*$", file.read(), 1, re.MULTILINE)
      item = toml.loads(frontmatter)
      item['content'] = markdown.markdown(content)
      item['slug'] = os.path.splitext(os.path.basename(file.name))[0]
      if config[content_type]["dateInURL"]:
        item['url'] = f"/{item['date'].year}/{item['date'].month:0>2}/{item['date'].day:0>2}/{item['slug']}/"
      else:
        item['url'] = f"/{item['slug']}"
      items.append(item)
  
    # sort in reverse chron order
    items.sort(key=lambda x: x[config[content_type]["sortBy"]],reverse=config[content_type]["sortReverse"])

    content_types = {}
    for content_type in config["types"]:
      content_types[config[content_type]['plural']] = load_content_type(content_type)
    
    return content_types

'''
load_template:
'''
def load_templates(template_directory):
  file_system_loader = jinja2.FileSystemLoader(template_directory)
  return jinja2.Environment(loader = file_system_loader)

'''
render_site: 
'''
def render_site(config, content, environment, output_directory):
  def render_type(content_type):
    #Post pages
    template = environment.get_template(f"{content_type}.html")
    for item in content[config[content_type]['plural']]:
      path = f"public/{item['url']}"
      pathlib.Path(path).mkdir(parents=True, exist_ok = True)
      with open(path+"index.html",'w') as file:
        file.write(template.render(this = item, config = config))

  if os.path.exists(output_directory):
    shutil.rmtree(output_directory)
  os.mkdir(output_directory)

  for content_type in config["types"]:
    render_type(content_type)
    
  #Homepage
  index_template = environment.get_template("index.html")
  with open(f"public/index.html",'w') as file:
    file.write(index_template.render(config = config, content = content))

  #Static files
  distutils.dir_util.copy_tree("static", "public")

def main():
 
  config = load_config("config.toml")
  # print(config)
  content = load_content_items(config, "content")
  environment = load_templates("layout")
  render_site(config, content, environment, "public")

main()