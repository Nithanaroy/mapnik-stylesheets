import os, sys, shutil
import generate_tiles as gt

# Can be obtained from https://github.com/gravitystorm/openstreetmap-carto.git
CARTO_STYLESHEET_PATH = './openstreetmap-carto.style'

# Postgres DB having Postgis extension
POSTGRES_DB = 'gis'

# Tiles output location
OUTPUT_DIR = './tiles'

# Bounding box for which the tiles have to be generated
# bbox = (-76, 58, --10, 84) # Greenland
bbox = (-130, 24, -98, 51) # US West

def clear_directory(path):
	for f in os.listdir(path):
		f = os.path.join(path, f)
		if os.path.isfile(f):
			os.unlink(f)
		else:
			shutil.rmtree(f)

def main():
	if len(sys.argv) < 2:
		# Can obtain country wise extracts from http://download.geofabrik.de/
		print 'Provide absolute directory path containing osm files as first argument'
		return

	directory = sys.argv[1]
	try:
		files = os.listdir(directory)
		index = 0
		for f in files:
			if f.endswith('.osm.pbf'):
				filepath = os.path.join(directory, f)
				print '\n\nInfo: Importing file, %s into Postgres' % (f,)
				os.system('osm2pgsql -d %s %s --style %s --slim --cache 4000 --number-processes 4' % (POSTGRES_DB, filepath, CARTO_STYLESHEET_PATH))

				print '\n\nInfo: Generating XML for file, %s from Postgres' % (f,)
				os.system('./generate_xml.py osm.xml  --dbname %s --host localhost --user postgres --accept-none > out.xml' % (POSTGRES_DB,))

				print '\n\nInfo: generating tiles for file, %s' % (f,)
				if index == 0:
					clear_directory(OUTPUT_DIR) # clear contents of output directory

				outdir = os.path.join(OUTPUT_DIR, str(index))
				os.mkdir(outdir)
				if not outdir.endswith('/'):
					outdir = outdir + '/'
				gt.render_tiles(bbox, 'out.xml', outdir, 1, 18)

				index += 1
	except Exception as ex:
		print ex

if __name__ == "__main__":
    main()
