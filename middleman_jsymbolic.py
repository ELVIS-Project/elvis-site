from lxml import etree
import requests
import json
import pickle



#note: the workflow to be used needs to be loaded in rodan manually before starting to use the following script
def get_rodan_token(username, password):
    token = requests.post('https://rodan.simssa.ca/auth/token/', data={'username': username, 'password': password})
    return json.loads(token.text)['token']

"""
Gets the urls of midi and mei files currently in the elvis database.
"""
def get_from_elvis(username, password):
    midimei_files_urls = []
    resp = requests.get('http://dev.database.elvisproject.ca/search/?filefilt=.midi&filefilt=.mei', auth = (username, password))
    pages = json.loads(resp.text)['paginator']['total_pages']
    for page in range(1,pages+1):
        print(page)
        search = requests.get('http://dev.database.elvisproject.ca/search/?filefilt[]=.midi&filefilt[]=.mei&page='+str(page), auth = (username, password))
        for object in json.loads(search.text)['object_list']:
            if 'pieces_searchable' in object.keys():
                piece = requests.get('http://dev.database.elvisproject.ca/piece/'+str(object['id'])+'?format=json', auth=(username, password))
                for attachment in json.loads(piece.text)['attachments']:
                    if attachment['extension'] == ".midi" or attachment['extension'] == ".mei":
                        midimei_files_urls.append(attachment['url'])
            else:
                movement = requests.get('http://dev.database.elvisproject.ca/movement/'+str(object['id'])+'?format=json', auth=(username, password))
                for attachment in json.loads(movement.text)['attachments']:
                    if attachment['extension'] == ".midi" or attachment['extension'] == ".mei":
                        midimei_files_urls.append([attachment['url'], attachment['extension']])
    with open('midi_urls', 'wb') as out_file:
            pickle.dump(midimei_files_urls, out_file)
    return midimei_files_urls

"""
Pushes the resulting feature files from the jsymbolic run into the appropriate places in the database
(entry corresponding to where the original file came from).
TODO: figure out what is preventing uploads to what should be the proper media file location on the backend.
"""
def push_to_elvis(results, token):
    results = pickle.load(open('rodan_results_urls', 'rb'))

    for page in results:
        for result in page:
            file_path = '/'.join(result['name'].split('@', 3)[:3])
            if result['resource_type'] == 'https://rodan.simssa.ca/resourcetype/f6c9e1a1-dd34-40f1-a898-c15914aa00d3/':
                file_name = ''.join((result['name'].split('@', 3)[3]+'.arff').split())
            elif result['resource_type']== 'https://rodan.simssa.ca/resourcetype/f4ba139d-6596-4ebd-861c-1ada8c4653df/':
                file_name = ''.join((result['name'].split('@', 3)[3]+'.csv').split())
            else:
                root = etree.XML(requests.get(result['resource_file'], headers={'Authorization': "Token "+token}).text)
                tree = etree.ElementTree(root)
                if 'feature_vector_file' in tree.docinfo.doctype:
                    file_name = ''.join((result['name'].split('@', 3)[3]+'_values'+'.xml').split())
                elif 'feature_key_file' in tree.docinfo.doctype:
                    file_name = ''.join((result['name'].split('@', 3)[3]+'_definitions'+'.xml').split())
                else:
                    print("Bad XML")
                    break
            files = {'files': requests.get(result['resource_file'], headers={'Authorization': "Token "+token}).content}
            resp = requests.put('http://127.0.0.1:8000'+'/media/attachments/'+file_path+'/', files=files, data={'file_path':'/'+file_path+'/', 'file_name': file_name}, auth=('', ''))

    return resp


"""
Download the files from the provided url list  and upload them into the appropriate rodan project as resources.

"""
def push_to_rodan(elvis_username, elvis_password, file_url_array, project_url, resourcetype, token):
    resources = []
    for url in file_url_array:
        files={'files': ('@'.join(url[0].split('/')[3:])+url[1],
                         requests.get('http://dev.database.elvisproject.ca'+url[0], auth=(elvis_username, elvis_password)))}
        resource_data={'project': project_url, 'type': resourcetype}
        resource_upload = requests.post('https://rodan.simssa.ca/resources/', files=files, data=resource_data, headers={'Authorization': "Token "+token})
        resources.append(json.loads(resource_upload.text['url']))
    return resources



"""
Load up the appropriate resources into the jsymbolic workflow, then run it, logging what goes wrong if it does.
TODO: re-create a proper logging mechanism
"""
def run_workflow(token, workflow_url, input_url):
    # resourcelist = []
    # for pageno in range(1,json.loads(requests.get('https://rodan.simssa.ca/',
    #                                               headers={'Authorization': "Token "+token}).text)['number_of_pages']+1):
    #     resources = requests.get(''.format(str(pageno)),
    #                              headers={'Authorization': "Token "+token})
    #     for i in json.loads(resources.text)['results']:
    #         print(i)
    #         resourcelist.append(i['url'])
        workflow_data = {"created": "null", "updated": "null", "workflow": workflow_url, "resource_assignments":
            {input_url: resourcelist},
                         "name": "jsymbolic_elvis", "description": "Run of Workflow jsymbolic_elvis"}
        workflow_run = requests.post('https://rodan.simssa.ca/workflowruns/', data=json.dumps(workflow_data), headers={'Content-Type': 'application/json','Authorization': "Token "+token})

    json.loads(workflow_run.text)['url']
    all_results = []
    initial_result = requests.get("https://rodan.simssa.ca/resources/?result_of_workflow_run={0}".format(""), headers={'Authorization': "Token "+token})
    for page in range(1, json.loads(initial_result.text)['total_pages']+1):
        results = requests.get("https://rodan.simssa.ca/resources/?page={0}&result_of_workflow_run={1}".format(str(page),""), headers={'Authorization': "Token "+token})
        print(results.text)
        all_results.append(json.loads(results.text)['results'])
    with open('rodan_results_urls', 'wb') as out_file:
        pickle.dump(all_results, out_file)


"""
Get the results from the jsymbolic workflow run  of all the previously uploaded files
"""
def get_from_rodan(resource_id):
    result = requests.get('https://rodan.simssa.ca/resources/?result_of_workflow_run='+str(resource_id), headers={})
    result_files = json.loads(result.text)['results']
    actual_files = []
    for results in result_files:
        file_location = results['resource_file']
        print(file_location)
        actual_files.append(requests.get(file_location, headers={}))
    return actual_files







if __name__ == "__main__":

#note: dummy usernames and password.
#TODO: "make usernames, passwords, project urls and workflow urls command-line enterable"
    current_token = get_rodan_token('rodan_username', 'rodan_password')
    midi_and_mei_urls = get_from_elvis('elvis_username', 'elvis_password')








