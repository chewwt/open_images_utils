import csv

# returns a set of classes in chosen csv file. Names are 
# automatically squeezed and converted to lowercase
def get_chosen(chosen):
    c = set()
    with open(chosen, 'r') as f:
        csvreader = csv.reader(f, delimiter=',')

        for row in csvreader:
            c.add(squeeze_lower(row[0]))
    return c

def squeeze_lower(name):
    return name.replace(' ', '').lower()