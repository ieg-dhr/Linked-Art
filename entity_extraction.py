import os, json

# Listing all .trig-Files in the given dir
dir = "data/Pharos-all_data/"  # for linux (check whether for  mac or eindows this is different)
file_names = os.listdir(dir)
files = []
for name in file_names:
    if os.path.isdir(dir + name):
        subfolder = os.listdir(dir + name + "/")
        for subname in subfolder:
            if os.path.isfile(dir + name + "/" + subname) & subname.__contains__(".trig"):
                files.append(name + "/" + subname)
dump_dict = {}

print(len(files))


# Iterating over each collected file 
for filename in files:
    print(filename)
    #loading the data of one file
    with open(dir+filename, encoding="utf8") as input_file:
        text_data = input_file.read()

    # clean the data of unwanted signs and split it in the several entities
    cleaned_and_splitted_data = text_data.replace("...", "_").replace(" .", "§").replace(" ", "").replace('";', '"~').replace(">;", ">~").replace('\\"', "'").replace("\n", "").replace("https://", "").replace("http://", "").split("}")

    # through splitting there will be elements without data. These elements will be excluded with the follwing lines
    indexes_to_pop = []
    for index, element in enumerate(cleaned_and_splitted_data):
        if len(element) <= 1:
            indexes_to_pop.append(index)
    indexes_to_pop = indexes_to_pop[::-1]
    for element in indexes_to_pop:
        cleaned_and_splitted_data.pop(element)

    # splitting the data into entities and attributes for every entitie
    cleaned_and_splitted_data_twice = [element.split("{") for element in cleaned_and_splitted_data]

    ###ENTITIES###
    # Splitting the entitie names
    cleaned_specifications = [listing[0].split("/") for listing in cleaned_and_splitted_data_twice]

    # taking the essential parts of the entity and the id
    pure_specifications = []
    for listing in cleaned_specifications:
        element = listing[-3]
        pure_specifications.append(element)

    pure_specification_ids = []
    for listing in cleaned_specifications:
        element = listing[-2]
        pure_specification_ids.append(element)

    # bringing both together
    pure_spec_dict = list(zip(pure_specification_ids, pure_specifications))
    for index in range(len(pure_spec_dict)):
        pure_spec_dict[index] = "{}({})".format(pure_spec_dict[index][0], pure_spec_dict[index][1])

    ###ATTRIBUTES###
    # seperating the attributes in an extra list
    cleaned_attributes = [listing[1] for listing in cleaned_and_splitted_data_twice if len(listing) > 1]

    # split the attributes and pop the last element, because it will be empty
    cleaned_and_splitted_attributes = [element.split("§") for element in cleaned_attributes]
    for element in cleaned_and_splitted_attributes:
        element.pop()

    # split the attributes again
    pure_attributes = []
    for listing in cleaned_and_splitted_attributes:
        attribute_list = []
        for list_element in listing:
            placebo = list_element.split("~")
            attribute_list.append(placebo)
        pure_attributes.append(attribute_list)

    # for each attribute there are three possibile ways to extract the essential data

    for index in range(len(pure_attributes)):
        for index_2 in range(len(pure_attributes[index])):
            for index_3 in range(len(pure_attributes[index][index_2])):
                """if filename == "formated-part_3128_cleaned.trig":
                    print(pure_attributes[index][index_2][index_3])"""
                if pure_attributes[index][index_2][index_3].__contains__(">a<"):

                    pure_attributes[index][index_2][index_3] = pure_attributes[index][index_2][index_3].split(">a<")

                    for index_4 in range(len(pure_attributes[index][index_2][index_3])):
                        pure_attributes[index][index_2][index_3][index_4] = pure_attributes[index][index_2][index_3][index_4].split("/")
                        if "graph" in pure_attributes[index][index_2][index_3][index_4]:
                            pure_attributes[index][index_2][index_3][index_4] = pure_attributes[index][index_2][index_3][index_4][-3:-1]
                        else:
                            pure_attributes[index][index_2][index_3][index_4] = pure_attributes[index][index_2][index_3][index_4][-2:]
                
                elif pure_attributes[index][index_2][index_3].__contains__("><"):

                    pure_attributes[index][index_2][index_3] = pure_attributes[index][index_2][index_3].split("><")

                    for index_4 in range(len(pure_attributes[index][index_2][index_3])):
                        pure_attributes[index][index_2][index_3][index_4] = pure_attributes[index][index_2][index_3][index_4].split("/")
                        if "graph" in pure_attributes[index][index_2][index_3][index_4][-1]:
                            pure_attributes[index][index_2][index_3][index_4] = pure_attributes[index][index_2][index_3][index_4][-3:-1]
                        else:
                            pure_attributes[index][index_2][index_3][index_4] = pure_attributes[index][index_2][index_3][index_4][-2:]

                else:
                    pure_attributes[index][index_2][index_3] = pure_attributes[index][index_2][index_3].split("\"")
                    pure_attributes[index][index_2][index_3] = pure_attributes[index][index_2][index_3][-2]



    # bringing both back together
    data_dict = {}
    for index in range(len(pure_spec_dict)):
        data_dict[pure_spec_dict[index]] = pure_attributes[index]

    for i in range(len(pure_spec_dict)):
        for index in range(len(data_dict[pure_spec_dict[i]])):
            for index_2 in range(len(data_dict[pure_spec_dict[i]][index])):
                if type(data_dict[pure_spec_dict[i]][index][index_2]) == list:
                    data_dict[pure_spec_dict[i]][index][index_2] = ("{}({})".format(data_dict[pure_spec_dict[i]][index][index_2][0][1], data_dict[pure_spec_dict[i]][index][index_2][0][0]), "{}({})".format(data_dict[pure_spec_dict[i]][index][index_2][1][1], data_dict[pure_spec_dict[i]][index][index_2][1][0]))
                if type(data_dict[pure_spec_dict[i]][index][index_2]) == str:
                    data_dict[pure_spec_dict[i]][index][index_2] = {"Label": data_dict[pure_spec_dict[i]][index][index_2]}
    
    dump_dict[filename] = data_dict

with open("data/entity_dump.json", "w") as dump_file:
    json.dump(dump_dict, dump_file, indent=4)


### Known issues ###
# During the final split and extraction of the attributes, elements with multiple values will only keep one value. This is known for some location values.
# In retrospect it would have been better if the data would be collected in a clean dictionary. It could be worth it, if someone new works with the data, to transform this code in this direction. But this would also include a rework of all code that follows. So it realy depends on how good you understand the structure of the given dictionary and the data as a whole.
