#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul  2 10:21:19 2020

@author: aiden
"""

import json
import urllib.request
import treelib

class GithubDirectoryTree:
    def __init__(self, repo_owner, repo_name):
        self.tree = treelib.Tree()
        self.tree.create_node("/", "/", data="directory")
        
        # retrieve data
        url = "https://api.github.com/repos/" + repo_owner + "/" + repo_name + "/git/trees/master?recursive=1"
        response = urllib.request.urlopen(url)
        data = json.load(response)

        # parse data and add paths to the tree
        paths = []
        for node in data.get("tree"):
            paths.append([node.get("path"), node.get("type")])
        
        for path, obj_type in paths:
            split = path.split("/")
            for item in split:
                full_name = "/" + "/".join(split[:(split.index(item) + 1)])
                parent_name = "/" + "/".join(split[:(split.index(item))])

                try:
                    if obj_type == "tree":
                        self.tree.create_node(item, full_name, parent_name, data="directory")
                    else:
                        self.tree.create_node(item, full_name, parent_name, data="file")
                except treelib.exceptions.DuplicatedNodeIdError:
                    pass
                
    def list_files(self, directory, **kwargs):
        files = []
        
        if len(directory) > 1:                # make sure '/' is in the correct locations to avoid seemingly
            directory = directory.strip("/")  # incorrect behaviour
            directory = "/" + directory
        
        if self.tree.get_node(directory).data != "directory":
            raise ValueError(directory + " is not a directory")
        
        for item in self.tree.children(directory):
            if item.data == "file":
                if (("." + item.identifier.split(".")[-1]) in kwargs.get("extensions", "")) or not kwargs.get("extensions"):
                    files.append(item.identifier)
                
        return files
    
    def isfile(self, file):
        if len(file) > 1:           # make sure '/' is in the correct locations to avoid seemingly
            file = file.strip("/")  # incorrect behaviour
            file = "/" + file
            
        if self.tree.get_node(file).data == "file":
            return True 
        elif not self.tree.get_node(file):  # if none then raise error
            raise ValueError(file + " does not exist")
        else:
            return False
        
    def isdir(self, directory):
        if len(directory) > 1:                     # make sure '/' is in the correct locations to avoid seemingly
            directory = directory.strip("/")  # incorrect behaviour
            directory = "/" + directory
            
        if self.tree.get_node(directory).data == "directory":
            return True 
        elif not self.tree.get_node(directory):  # if none then raise error
            raise ValueError(directory + " does not exist")
        else:
            return False
        
    def listdir(self, directory):
        items = []
        
        if len(directory) > 1:                # make sure '/' is in the correct locations to avoid seemingly
            directory = directory.strip("/")  # incorrect behaviour
            directory = "/" + directory
        
        if self.tree.get_node(directory).data != "directory":
            raise ValueError(directory + " is not a directory")
        
        for item in self.tree.children(directory):  
            items.append(item.identifier)
            
    def split_file(self, file):
        if len(file) > 1:           # make sure '/' is in the correct locations to avoid seemingly
            file = file.strip("/")  # incorrect behaviour
            file = "/" + file
            
        if self.tree.get_node(file).data == "file":
            file = file.split("/")[-1]
            file = file.split(".")[:-1]
            return file[0] 
        elif not self.tree.get_node(file):  # if none then raise error
            raise ValueError(file + " does not exist")
        else:
            raise ValueError(file + " is not a file")
            
            
if __name__ == "__main__":
    g = GithubDirectoryTree("CSSEGISandData", "Covid-19")
    g.tree.show()
    for file in g.list_files("/who_covid_19_situation_reports/who_covid_19_sit_rep_pdfs", extensions=[".pdf"]):
        print(g.split_file(file))
    print(g.split_file("/.gitignore"))