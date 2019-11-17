#! /usr/bin/env python3
'''
cumulonimbus v0.1 - Copyright 2019 James Slaughter,
This file is part of cumulonimbus v0.1.

cumulonimbus v0.1 is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

cumulonimbus v0.1 is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with cumulonimbus v0.1.  If not, see <http://www.gnu.org/licenses/>.
'''

'''
This project builds heavily on the work of Cloudscraper by @ok_bye_now
https://github.com/jordanpotti/CloudScraper
'''

#python import
import sys
import os
import datetime
import time
import json
import itertools
import requests
import sys
import re
from argparse import ArgumentParser
from multiprocessing import Pool
from termcolor import colored
from rfc3987 import parse

#programmer generated imports
from controller import controller
from fileio import fileio

'''
Usage()
Function: Display the usage parameters when called
'''
def Usage():
    print ('Usage: [required] --[target|targetlist] --[domains|files] [optional] --depth --process --output --debug --help')
    print ('Example: cumulonimbus.py --targetlist targetlist.txt --domains --depth 2 --process 5 --debug')
    print ('Required Arguments:')
    print ('--[target|targetlist] - The single or list of targets to be reviewed')
    print ('--[domains|files] - Searching for cloud resources or specific imported media types')
    print ('Optional Arguments:')
    print ('--depth - info should be used by default but additional types can be set in the whoisdl.conf.')
    print ('--process - all or specific')
#   print ('--output - Location and filename where the output is to be deposited')
    print ('--debug - Prints verbose logging to the screen to troubleshoot issues with a recon installation.')
    print ('--help - You\'re looking at it!')
    sys.exit(-1)

'''
ConfRead()
Function: - Reads in the cumulonimbus.conf config file and assigns some of the important
            variables
'''
def ConfRead():
        
    ret = 0
    intLen = 0
    FConf = fileio()
    data = ''

    try:
        #Conf file hardcoded here
        with open('/opt/cumulonimbus/cumulonimbus.conf', 'r') as read_file:
            data = json.load(read_file)    
    except Exception as e:
        print (e)
        print ('[x] Unable to read configuration file  Terminating...\n')
        return -1    

    CON.logfile = data['logfile']   
    CON.cloud_domains = data['cloud_domains']
    CON.file_types = data['file_types']
    CON.depth = data['depth']
    CON.process = data['process']
    CON.user_agent =data['user_agent'] 
  
    if (CON.debug == True):
        print ('[DEBUG] data: ', data)
        print ('[DEBUG] CON.logfile: ' + str(CON.logfile))
        print ('[DEBUG] CON.cloud_domains: ' + str(CON.cloud_domains))
        print ('[DEBUG] CON.file_types: ' + str(CON.file_types))
        print ('[DEBUG] CON.depth: ' + str(CON.depth))
        print ('[DEBUG] CON.process: ' + str(CON.process))
        print ('[DEBUG] CON.user_agent: ' + str(CON.user_agent))
 
        #for a_cloud_domains in CON.cloud_domains: 
        #    for key, value in a_cloud_domains.items():
        #        print ('[DEBUG] CON.cloud_domains key: ' + key + ' value: ' + value)

        #for a_file_types in CON.file_types: 
        #    for key, value in a_file_types.items():
        #        print ('[DEBUG] CON.file_types key: ' + key + ' value: ' + value)
            
    if (CON.debug == True):
       print ('[*] Finished configuration.')
       print ('')
  
    #Get logging going...
    if not (os.path.isfile(CON.logfile)):
        FLOG = open(CON.logfile, "w")
        FLOG.write('[*] Creating log file...\n')
        FLOG.close()
        CON.FLOG = open(CON.logfile, "a")
    else:
        CON.FLOG = open(CON.logfile, "a") 

    print ('[*] Executing cumulonimbus v0.1... ')
    CON.FLOG.write('[*] Executing cumulonimbus v0.1...\n')
         
    print ('[*] Finished configuration successfully.\n')
    CON.FLOG.write('[*] Finished configuration successfully.\n')

    return 0

'''
Parse() - Parses program arguments
'''
def Parse(args):        
    option = ''
                    
    print ('[*] Arguments: \n')
    for i in range(len(args)):
        if args[i].startswith('--'):
            option = args[i][2:]  

            if option == 'targetlist':
                CON.targetlist = args[i+1]
                print (option + ': ' + str(CON.targetlist))

            if option == 'target':
                CON.target = args[i+1]
                print (option + ': ' + str(CON.target))

            if option == 'domains':
                CON.domains = True
                print (option + ': ' + str(CON.domains))

            if option == 'files':
                CON.files = True
                print (option + ': ' + str(CON.files))

            if option == 'depth':
                CON.depth = args[i+1]
                print (option + ': ' + str(CON.depth))

            if option == 'process':
                CON.process = args[i+1]
                print (option + ': ' + str(CON.process))

            #if option == 'output':
            #    CON.output = args[i+1]
            #    print (option + ': ' + CON.output)

            if option == 'debug':
                CON.debug = True
                print (option + ': ' + str(CON.debug))

            if option == 'help':
                return -1

    if (CON.depth == ''):
        print ('[-] Depth flag not used.  Default depth of 3 will be used...')
        print ('')

    if (CON.process == ''):
        print ('[-] Process flag not used.  Default process of 5 will be used...')
        print ('')

    #These are required params so length needs to be checked after all 
    #are read through  
    if ((len(CON.targetlist) < 3) and (len(CON.target) < 3 )):
        print ('[x] --target or --targetlist must be included in the arguments')
        print ('')
        return -1

    if ((len(CON.targetlist) >= 3) and (len(CON.target) >= 3 )):
        print ('[x] --target or --targetlist may only be used one at a time')
        print ('')
        return -1

    if ((CON.domains == False) and (CON.files == False)):
        print ('[x] --domains or --files must be included in the arguments...')
        print ('')
        return -1

    if ((CON.domains == True) and (CON.files == True)):
        print ('[x] --domains or --files may only be used one at a time...')
        print ('')
        return -1
  
    return 0

'''
checker() - Check if the url is a valid one or not.
'''
def checker(url):

    try:
        parse(url)
        return True
    except ValueError:
        return False
    return False

'''
gather_links() - Apply to the raw HTML a regular expression to gather all the urls.
'''
def gather_links(html):

    urls = []
    links_ = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', html)
    urls.extend(filter(checker, links_)) #filter the ones that don't compile with the checker function

    del(links_)
    return list(set(urls))

'''
start() - Load the initial url and gather the first urls that will be used
          by the spider to keep looking for more links
'''
def start(target):

    if (CON.domains == True):
        print(colored('[*] Beginning search for cloud resources in {}\n'.format(target), color='cyan', attrs=['bold']))
        CON.FLOG.write('[*] Beginning search for cloud resources in {}\n'.format(target))

    if (CON.files == True):
        print(colored('[*] Beginning search for file resources in {}\n'.format(target), color='cyan', attrs=['bold']))
        CON.FLOG.write('[*] Beginning search for file resources in {}\n'.format(target))

    try:
        html = requests.get(target, allow_redirects=True, headers=headers).text
        #html = requests.get(target, allow_redirects=True, headers=CON.user_agent).text
        links = gather_links(html)
    except requests.exceptions.RequestException as e:
        if (CON.debug == True):
            print(colored('[x] Network error: {}'.format(e), color='red', attrs=['bold']))
            CON.FLOG.write('[x] Network error: {}'.format(e))
        return -1

    print(colored('[*] Initial links: {}\n'.format(len(links)), color='cyan', attrs=['bold']))
    CON.FLOG.write('[*] Initial links: {}\n'.format(len(links))) 
    spider(links, target)

'''
worker() - Function handling all the crawling action of the spider.
           It first checks the desired depth and if the domain of
           the url matches the target to avoid crawling other web sites.
           Makes a GET request, parses the HTML and returns all the links.
'''
def worker(url):

    if url.count("/") <= int(CON.depth) + 2:
        try:
            html = requests.get(url, allow_redirects=True, headers=headers).text
            #html = requests.get(url, allow_redirects=True, headers=CON.user_agent).text 
            links = gather_links(html)

        except requests.exceptions.RequestException as e:
            if (CON.debug == True):
                print(colored('[x] Network error: {}'.format(e), color='red', attrs=['bold']))
                CON.FLOG.write('[x] Network error: {}'.format(e))                
            return []

        try:
            print('[*] {} links found [{}]'.format(len(links), url))
            CON.FLOG.write('[*] {} links found [{}]'.format(len(links), url) + '\n')
        except Exception as e:
            # Unicode issue?!
            print (e)            
            print ('[x] Unable print link\n')
            CON.FLOG.write('[x] Unable print link')
            return []

        return links

    else:
        return []
        

'''
spider() - Loop through the initial links found in the given page. Each new link
           discovered will be added to the list if it's not already there, and thus
           crawled aswell looking for more links.

           wannabe list works as the placeholder for the urls that are yet to crawl.
           base_urls is a list with all the already crawled urls.
'''
def spider(base_urls, target):

    global target_
    target_ = parse(target)
    p = Pool(int(CON.process))
    wannabe = [url for url in base_urls if target_['authority'] in parse(url)['authority']]

    while True:
        try:
            #retrieve all the urls returned by the workers
            new_urls = p.map(worker, wannabe)
            #flatten them and remove repeated ones
            new_urls = list(set(itertools.chain(*new_urls)))
            wannabe = []
            i = 0
 
            #if new_urls is empty meaning no more urls are being discovered, exit the loop
            if new_urls == []:
                break
        
            else:
                for url in new_urls:
                    if url not in base_urls:
                        '''
                        For each new url, check if it hasn't been crawled. If it's 
                        indeed new and contains the target domain it gets appended to 
                        the wannabe list so in the next iteration it will be crawled. 
                        '''
                        i += 1
                        if target_['authority'] in parse(url)['authority']:
                            wannabe.append(url)
                        base_urls.append(url)
        except Exception as e:
            print('[x] Unable to print link - ' + str(e) + '\n')
            break
        
        print(colored('\n[*] New urls appended: {}\n'.format(i), 'green', attrs=['bold']))
        CON.FLOG.write('\n[*] New urls appended: {}\n'.format(i))

    #once all the links for the given depth have been analyzed, execute the parser
    parser(base_urls)

'''
parser() - Once all the links have been gathered check how many of them
           match with the list of cloud domains we are interested in.
'''
def parser(links):

    print(colored('[*]Parsing results...', color='cyan', attrs=['bold']))
    CON.FLOG.write('[*] There were no matches!\n')
    matches = []

    if (CON.domains == True):
        [[matches.append(link) for link in links if cloud_domain in link] for cloud_domain in CON.cloud_domains]
        matches = list(set(matches))

    if (CON.files == True):
        [[matches.append(link) for link in links if file_type in link] for file_type in CON.file_types]
        matches = list(set(matches))
    
    print('\n[*] Total links: ' + str(len(links)) + '\n')

    if (len(matches) == 0):
        print(colored('[-] There were no matches!\n', 'red', attrs=['bold']))
        CON.FLOG.write('[-] There were no matches!\n')
    
    else:
        print(colored('[*] There was/were {} match(es) for this search!\n'.format(len(matches)), 'green', attrs=['bold']))
        CON.FLOG.write('[*] There was/were {} match(es) for this search!\n'.format(len(matches)))
        [print('[-]', match, '\n') for match in matches]
        [CON.FLOG.write('[-]'+ match + '\n') for match in matches]

'''
cleaner() - adds https into a url if it doesn't already have it.
'''
def cleaner(url):
    if 'http' not in url:
        return ("https://"+url).rstrip()
    else:
        return url

'''
Terminate()
Function: - Attempts to exit the program cleanly when called  
'''     
def Terminate(exitcode):
    sys.exit(exitcode)


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}

'''
This is the mainline section of the program and makes calls to the 
various other sections of the code
'''
if __name__ == '__main__':

    ret = 0 
    count = 0  

    CON = controller() 

    ret = Parse(sys.argv)
    if (ret == -1):
        Usage()
        Terminate(ret)

    ret = ConfRead()
    # Something bad happened...bail
    if (ret != 0):
        Terminate(ret)

    if (len(CON.targetlist) > 3): 
        try:
            print ('[*] Reading targetlist file: ' + CON.targetlist + '\n')
            CON.FLOG.write('[*] Reading targetlist file: ' + CON.targetlist + '\n')
            # Read in our list of targets
            with open(CON.targetlist.strip(),"r") as CON.target_list:
                [start(cleaner(line)) for line in CON.target_list]                
        except Exception as e:
            # Target list read failed, bail!
            print (e)            
            print ('[x] Unable to read targetlist file: ' + CON.targetlist + '\n')
            CON.FLOG.write('[x] Unable to read targetlist: ' + CON.targetlist + '\n') 
    else:
        start(cleaner(CON.target))

    print(colored('***Program Complete***', 'green', attrs=['bold']))
    CON.FLOG.write('***Program Complete***')
    Terminate(0)

'''
END OF LINE
'''
