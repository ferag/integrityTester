#!/usr/bin/python
import requests
import json
import urllib2
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import hashlib
import pandas as pd
import config as cfg

#This function is for seeing the different elements on the XML
def listElemnts(iterator):
    for elem in iterator:
        elemList.append(elem.tag) # indent this by tab, not two spaces as I did here

    # now I remove duplicities - by convertion to set and back to list
    elemList = list(set(elemList))

    # Just printing out the result
    i = 1
    for elem in elemList:
        print "%i. %s" % (i,elem)
        i = i + 1

#Check 1 - cheksum of the file
def md5sum(remote, max_file_size=100*1024*1024):
    hash = hashlib.md5()

    total_read = 0
    while True:
        data = remote.read(4096)
        total_read += 4096

        if not data or total_read > max_file_size:
            break

        hash.update(data)

    return hash.hexdigest()

def main():
    fairness_index = 0 #fairness index
    findable = False
    accessible = False
    interoperable = False
    reusable = False
    ## Plan
    print("######### Test#0 Begins: Plan")
    print("######### Description: checks Data Management Plan existance in Metadata")
    plan = raw_input("Is there any link to DMP? Please indicate DOI\n")
    if "https" not in plan:
        plan = 'https://doi.org/'+plan
    exist = requests.get(plan) 
    if exist.status_code != 200 or plan == 'https://doi.org/':
        print("DMP does not exist")
        print('\x1b[5;37;41m' + 'Test #0 FAILED' + '\x1b[0m')
    else:
        print("DMP found")
        print plan
        print('\x1b[6;30;42m' + 'Test#0 OK' + '\x1b[0m')
        fairness_index += 1 
    ## Collect
    print("######### Test#1 Begins: Collect")
    print("######### Description: Checks metadata and if data is not empty")
    #Adding access token
    ACCESS_TOKEN = cfg.params['ACCESS_TOKEN']
    #Searching metadata files. Metadata word as query
    r = requests.get(cfg.params['API_URL'], params={'q': 'Metadata', 'access_token': ACCESS_TOKEN})
    index = 0
    for i in r.json():
        for key, value in i.iteritems():
            if key == 'title':
	         print '[%i] %s' % (index,value)
        index = index + 1

    selected_index = ''
    while(True):
        selected_index = raw_input("Select one of the metadata documents above\n")
        try:
            r.json()[int(selected_index)]
            break
        except Exception, e:
            print "Select a correct index"

    retrieving = r.json()[int(selected_index)]['links']['bucket']

    p = requests.get(retrieving,params={'access_token': ACCESS_TOKEN})
    file_url=p.json()['contents'][0]['links']['self']

    file_name = file_url.split('/')[-1]
    u = urllib2.urlopen(file_url+"?access_token="+ACCESS_TOKEN)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,
   
    f.close()
    fr = open(file_name,'r') 
    xmlTree = ET.parse(fr)

    elemList = []
    iterator = xmlTree.iter()

    url_function = '' # Stores the function related to the url.

    root = xmlTree.getroot()

    for url in root.iter('url'):
        print "Downloading file: %s" % url.text
        url_function = url.get('function')
    fr.close() #Close the file

    #If defined function is download, the url is downloable
    if url_function == 'download':

        #Integrity test 0: existance
        download = url.text
        try:
            response = urllib2.urlopen(download)
        except urllib2.HTTPError, e:
            print 'Test #1.1 FAILED'
            print('\x1b[5;37;41m' + 'Test #1 FAILED' + '\x1b[0m')
            print 'Dataset does not exists'
            fairness_index -= 1
            exit()
        print('\x1b[6;30;42m' + 'Test #1.1 OK' + '\x1b[0m')
        fairness_index += 1
        print("######### Test#1.2 Begins: Collect - Checksum")
        #Integrity test 1: checksum 
        check1metadata = ''
        check1dataset = ''

        #Authentication is the element where the checksum goes in EML
        for chksum in root.iter('authentication'):
            check1metadata = chksum.text
        check1dataset = md5sum(response)

        if check1metadata == check1dataset:
            print('\x1b[6;30;42m' + 'Test #1.2 OK' + '\x1b[0m')
            fairness_index += 1
        else:
            print('\x1b[5;37;41m' + 'Test #1.2 FAILED' + '\x1b[0m')
            print 'Dataset have been changed!'
            exit()
        ## Curate
        print("######### Test#2 Begins: Curate")
        print("######### Description: Checks Qc/Qa procedures description in Metadata")
        #Test if there is any description of Qc/Qa in metadata
        curate = raw_input("Is there any field in metadata describing Qc/Qa procedures? Please indicate\n")
        qcqa = 0
        for attribute in root.iter(curate):
                qcqa = qcqa + 1

        if qcqa > 0:
            print "Qc/Qa"
            print('\x1b[6;30;42m' + 'Test #2 OK' + '\x1b[0m')
            fairness_index += 1
        else:
            print('\x1b[5;37;41m' + 'Test #2 FAILED' + '\x1b[0m')

        print("######### Test#3.1 Begins: Analyze")
        print("######### Description: Checks if data is analyzable. Presence/Absence of parameters described in Metadata in Data")
        response = urllib2.urlopen(download)
        df = pd.read_csv(response, delimiter=';')
        print df.columns
        #The name of the parameter in the file is described in attributeLabel elements
        for attribute in root.iter('attributeLabel'):
            print attribute.text
            if attribute.text in df.columns:
                print 'OK'
                interoperable = True
            else:
                print('\x1b[5;37;41m' + 'Test #3 FAILED' + '\x1b[0m')
                fairness_index -= 1
                print 'Bad-defined parameters'
                interoperable = False
                exit()

        print('\x1b[6;30;42m' + 'Test #3.1 OK' + '\x1b[0m')
        fairness_index += 1
        print("######### Test#3.1 Begins: Checks is data is processable")
        print("######### Description: Checks if data can be processed (Temporal test)")
        #Hardcoded parameters, just for testing
        Temp = list(df['Temp'])
        date = list(df['date'])
        plt.scatter([pd.to_datetime(d) for d in date],Temp), plt.title('Title'), plt.ylabel('Temp'), plt.xlabel('dates'), plt.show()

        ## Ingest
        print("######### Test#4 Begins: Ingest")
        print("######### Description: Checks the existance of Persistent Identifiers assigned")
        plan = raw_input("Is there any PID or DOI assigned? Please indicate the metadata field where it is linked or the ID\n")
        doi = plan
        for attribute in root.iter(plan):
            doi = attribute.text
        if "https" not in doi:
            doi = 'https://doi.org/'+doi
        exist = requests.get(doi)
        if exist.status_code != 200 or plan == 'https://doi.org/':
            print("Identifier does not exist")
            print('\x1b[5;37;41m' + 'Test #4 FAILED' + '\x1b[0m')
        else:
            print("Identifier found")
            print doi
            print('\x1b[6;30;42m' + 'Test #4 OK' + '\x1b[0m')
            findable = True
            fairness_index += 1

        #Preserve
        print("######### Test#5 Begins: Preserve")
        print("######### Description: Checks the Data license")
        plan = raw_input("Is there any license assigned? Please indicate the metadata field where it is described\n")
        license = ''
        for attribute in root.iter(plan):
            license = attribute.text
        if license == '':
            print("License does not assigned")
            print('\x1b[5;37;41m' + 'Test #5.1 FAILED' + '\x1b[0m')
        else:
            print("License assigned")
            print license
            reusable = True
            print('\x1b[6;30;42m' + 'Test #5.1 OK' + '\x1b[0m')
            fairness_index += 1

        print("######### Test#5.2 Begins: Preserve - OAI-PMH")
        print("######### Description: Checks OAI-PMH existance")
        exist = requests.get(cfg.params['OAI-PMH']+'?verb=Identify')
        if exist.status_code != 200:
            print("OAI-PMH does not exist")
            print('\x1b[5;37;41m' + 'Test #5.2 FAILED' + '\x1b[0m')
        else:
            print("OAI-PMH found")
            print('\x1b[6;30;42m' + 'Test #5.2 OK' + '\x1b[0m')
            fairness_index += 1

        print("######### Test#5.3 Begins: OAI-PMH Access")
        print("######### Description: Checks if dataset is accessible with DOI")
        doi = doi.rsplit('.',1)[1]
	#identifier only will work with zenodo repos
	
        try:
            oai = urllib2.urlopen(cfg.params['OAI-PMH']+'?verb=GetRecord&metadataPrefix=oai_dc&identifier='+cfg.params['OAI-PMH-ID-FORM']+doi)
            xmlTree = ET.fromstring(oai.read())

            elemList = []
            iterator = xmlTree.iter()

            for elem in iterator:
                if 'iden' in elem.tag:
                    print elem.text
            print("Object found via OAI-PMH")
            print('\x1b[6;30;42m' + 'Test #5.3 OK' + '\x1b[0m')
            accessible = True
            fairness_index += 1
        except urllib2.HTTPError, e:
            print("Object not found via OAI-PMH")
            print('\x1b[5;37;41m' + 'Test #5.3 FAILED' + '\x1b[0m')

    #Summary
    print "######################################################################"
    print "FAIRness Level: %.0f%%" % (100 * fairness_index/8)
    if findable:
        print('\x1b[6;30;42m' + 'Findable' + '\x1b[0m')
    else:
        print('\x1b[5;37;41m' + 'NOT Findable' + '\x1b[0m')

    if accessible:
        print('\x1b[6;30;42m' + 'Accessible' + '\x1b[0m')
    else:
        print('\x1b[5;37;41m' + 'NOT Accessible' + '\x1b[0m')

    if interoperable:
        print('\x1b[6;30;42m' + 'Interoperable' + '\x1b[0m')
    else:
        print('\x1b[5;37;41m' + 'NOT Interoperable' + '\x1b[0m')

    if reusable:
        print('\x1b[6;30;42m' + 'Re-usable' + '\x1b[0m')
    else:
        print('\x1b[5;37;41m' + 'NOT Re-usable' + '\x1b[0m')

if __name__ == "__main__":
    main()
