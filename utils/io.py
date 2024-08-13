import csv

def write_to_csv(dirName,fileName, data):
    with open(f"./{dirName}/{fileName}.csv", "a", newline="\n",) as fd:
        writer_object = csv.writer(fd)
        writer_object.writerow(data)