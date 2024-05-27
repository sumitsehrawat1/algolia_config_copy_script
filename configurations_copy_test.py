from algoliasearch.search_client import SearchClient
import json
import os

org_name = os.environ.get("ORG_NAME", "")

source_index_name = os.environ.get("SRC_IDX_NAME", "")
source_index_api_key = os.environ.get("SRC_IDX_API_KEY", "")
source_index_api_secret = os.environ.get("SRC_IDX_API_SECRET", "")

target_index_name = os.environ.get("TGT_IDX_NAME", "")
target_index_api_key = os.environ.get("TGT_IDX_API_KEY", "")
target_index_api_secret = os.environ.get("TGT_IDX_API_SECRET", "")

source_env = os.environ.get("SRC_ENV", "")
target_env = os.environ.get("TGT_ENV", "")

# source_index_name = "uat_ajio_b2b"
# target_index_name = "prod_ajio_b2b"

# org_name = "AJIO"

# source_env = "UAT"
# target_env = "PROD"

src_client = SearchClient.create(source_index_api_key, source_index_api_secret)
target_client = SearchClient.create(target_index_api_key, target_index_api_secret)

# replica disctionary
replica_dict = {"virtual": set(), "normal": set()}

# for virtual replica only
keys_to_remove_virtual = ["replicas","attributeForDistinct", "attributesForFaceting", "optionalWords", "searchableAttributes", "numericAttributesForFiltering", "separatorsToIndex", "ranking", "renderingContent"]

# for standard indexes
keys_to_remove_standard = ["replicas", "renderingContent"]

def get_replica_name(replica, type):
    if(source_env!="" and ('_' + org_name+'_'+source_env) in replica):
        replica = replica.replace(('_' + org_name+'_'+source_env), "")
    idx_to_add = len(replica)
    if(type=='virtual'):
        idx_to_add = idx_to_add - 1
    replica = replica[:idx_to_add] + ('_' + org_name+'_'+target_env) + replica[idx_to_add:]
    return replica

def removeVirtualKeyword(replica_name):
    if('virtual(' in replica_name):
        idx_end = len(replica_name) - 1
        replica_name = replica_name[8:idx_end]
    return replica_name

def get_replica_names(source_index):
    source_replicas = source_index.get_settings()['replicas']
    for replica in source_replicas:
            if(replica.startswith('virtual(')):
                replica_dict["virtual"].add(replica)
            else:
                replica_dict["normal"].add(replica)
    print("replica_dict : {}".format(replica_dict))

def copyReplicas(target_index):
    replica_list = []
    for type, replica_set in replica_dict.items():
        for replica in replica_set:
            replica_list.append(get_replica_name(replica,type))
    target_index.set_settings({'replicas' : replica_list})
    print("replica created on clone : {}".format(replica_list))
    print("replica created on clone : {}".format(json.dumps(target_index.get_settings()['replicas'],indent=4)))

def copyIndex(source_index, target_index, type):
    settings_to_copy = source_index.get_settings()
    keys_to_remove = []
    if(type=='virtual'):
        keys_to_remove = keys_to_remove_virtual
    if(type=='normal'):
        keys_to_remove = keys_to_remove_standard
    for key in keys_to_remove:
        settings_to_copy.pop(key, None)
    target_index.set_settings(settings_to_copy)

def copyPrimaryIndex():
    source_index = src_client.init_index(source_index_name)
    target_index = target_client.init_index(target_index_name)

    copyIndex(source_index,target_index,'normal')
    print("replica {} cloned to {}".format(source_index,target_index))
    get_replica_names(source_index)
    copyReplicas(target_index)

    for type, replica_set in replica_dict.items():
        for replica in replica_set:
            target_replica_name = removeVirtualKeyword(get_replica_name(replica,type))
            source_replica_name = removeVirtualKeyword(replica)
            src_replica_idx = src_client.init_index(source_replica_name)
            tgt_replica_idx = target_client.init_index(target_replica_name)
            print("cloning replica {} to {}".format(replica,target_replica_name))
            copyIndex(src_replica_idx,tgt_replica_idx,type)
            print("replica {} cloned to {}".format(replica,target_replica_name))

copyPrimaryIndex()