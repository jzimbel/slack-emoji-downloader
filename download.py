from sys import argv
import os
import json
import requests
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
  failures = {}
  for name, url in originals.items():
    # Prints a download progress message that updates in place
    print(f'\r{counter+1:>6,} / {downloadCount:,}\t{to30Chars(name)}', end='')
    try:
      download(name, url)
    except:
      failures[name] = url
    counter += 1

  print('\n\nCreating symlinks for aliases')
  print('Some of these may fail if they refer to one of Slack\'s default emoji\n')
  for name, alias in aliases.items():
    resolvedAlias = resolveAlias(alias, originals, aliases)
    if resolvedAlias is not None:
      extension = getExtension(originals[resolvedAlias])
      symlink(f'{name}.{extension}', f'{resolvedAlias}.{extension}')

  print(f'\nDone. Images and aliases saved to {OUTPUT_PATH}.')

  if len(failures) > 0:
    failuresPath = f'{os.getcwd()}/failures.json'
    with open(failuresPath, 'w') as f:
      json.dump({'emoji': failures}, f, indent=4)
    print(f'\n{len(failures)} images failed to download. These have been recorded in {failuresPath}.')
    print('To retry these, rename the output directory to something else and then run:')
    print(f'python {argv[0]} {failuresPath}')

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
  Separates the emoji dict into new dictionaries containing originals and aliases, and returns both.
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
    raise Exception('Download failed')

def getExtension(url):
  return url.split('.')[-1]

def resolveAlias(alias, originals, aliases):
  '''
  Resolves an alias to the original that it refers to.
  Aliases can refer to other aliases, so this keeps going down the reference
  chain until it finds an original.
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
  Link target is relative so that moving/renaming the parent directory does not break the link.
  '''
  targetPath = f'{OUTPUT_PATH}/{targetName}'
  linkPath = f'{OUTPUT_PATH}/{linkName}'
  if os.path.isfile(targetPath):
    os.symlink(targetName, linkPath)
  else:
    print(f'Tried to create an alias symlink to {targetPath}, but it doesn\'t exist')

def to30Chars(s):
  '''
  Forces a string to 30 characters, padding with spaces or truncating as needed.
  '''
  if len(s) > 30:
    return s[:27] + '...'
  else:
    return s.ljust(30, ' ')

if __name__ == '__main__':
  main()
