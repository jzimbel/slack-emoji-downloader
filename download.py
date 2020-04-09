from sys import argv
import os
import json
import requests
import time
import shutil

OUTPUT_PATH = f'{os.getcwd()}/output'

def main():
  try:
    path = argv[1]
  except:
    print('No emoji JSON file supplied')
    return

  prepareOutput()

  originals, aliases = separate(getEmojiDict(path))
  downloadCount = len(originals)

  print('Downloading images')
  counter = 0
  for name, url in originals.items():
    print(f'{counter+1:>6,} / {downloadCount:,}', end='\r')
    download(name, url)

    if counter % 100 == 99:
      time.sleep(1)
    counter += 1
  print('\n')

  print('Creating symlinks for aliases')
  print('Some of these may fail if they refer to one of Slack\'s default emoji\n')
  for name, alias in aliases.items():
    resolvedAlias = resolveAlias(alias, originals, aliases)
    if resolvedAlias is not None:
      extension = getExtension(originals[resolvedAlias])
      symlink(f'{name}.{extension}', f'{resolvedAlias}.{extension}')

  print()
  print('Done.')

def prepareOutput():
  shutil.rmtree(OUTPUT_PATH, ignore_errors=True)
  os.makedirs(OUTPUT_PATH)

def getEmojiDict(path):
  '''
  Loads emoji names and urls from the supplied JSON file into a dict and returns it.
  '''
  with open(path) as f:
    return json.load(f)['emoji']

def separate(emojiDict):
  '''
  Separates the original emoji dict into new dictionaries containing originals and aliases, and returns both.
  '''
  originals = {}
  aliases = {}

  for name, url in emojiDict.items():
    if url.startswith('alias:'):
      aliases[name] = url.split(':')[1]
    else:
      originals[name] = url

  return originals, aliases

def download(name, url):
  '''
  Downloads an emoji image to a file in the output directory.
  '''
  extension = getExtension(url)
  path = f'{OUTPUT_PATH}/{name}.{extension}'

  r = requests.get(url)
  if r.status_code == 200:
    with open(path, 'wb') as f:
      f.write(r.content)
  else:
    print(f'Download failed: :{name}: @ {url}')

def getExtension(url):
  return url.split('.')[-1]

def resolveAlias(alias, originals, aliases):
  '''
  Resolves an alias to the original that it refers to. Aliases can refer to other aliases, so this needs to be recursive.
  '''
  if alias in originals:
    return alias
  if alias in aliases:
    return resolveAlias(aliases[alias], originals, aliases)
  print(f'Alias target not found: {alias}')
  return None

def symlink(linkName, targetName):
  '''
  Creates a symlink from an alias to the original image it refers to.
  '''
  # os.symlink's arguments are confusingly "backward":
  # first arg is the file we're linking TO, second arg is the name of the link.
  os.symlink(f'{OUTPUT_PATH}/{targetName}', f'{OUTPUT_PATH}/{linkName}')

if __name__ == '__main__':
  main()
