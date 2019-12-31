export organisation_csv=http://localhost:8000/organisation-collection/collection/organisation.csv
export organisation_tag_csv=http://localhost:8000/organisation-collection/data/tag.csv

make

while inotifywait -e close_write ../organisation-collection/collection/organisation.csv
do
  make
done
