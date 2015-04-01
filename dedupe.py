import csv
import sys


if __name__ == '__main__':
	inFile = open(sys.argv[1], 'rb')
	reader = csv.reader(inFile)
	
	outFile = open(sys.argv[1][:-4]+'_deduped.csv', 'wb')
	writer = csv.writer(outFile)
	
	map = {}
	
	for row in reader:
		url = row[0].strip()
		row[4] = row[4].strip().strip(',')
		if url not in map:
			map[url] = []
		map[url].append(row)
		
	inFile.close()
	
	for url in map:
		if len(map[url]) == 1:
			if row[2].strip() != '':
				writer.writerow(map[url][0])
		else:
			found = False
			for row in map[url]:
				if row[2].strip() != '':
					found = True
					writer.writerow(row)
					break
		
	outFile.close()