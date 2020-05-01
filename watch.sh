export organisation_csv=http://localhost:8000/organisation-dataset/collection/organisation.csv
export organisation_tag_csv=http://localhost:8000/organisation-dataset/data/tag.csv

make

while inotifywait -e close_write ../organisation-dataset/collection/organisation.csv
do
  make
done
