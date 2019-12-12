# start_wars_api_etl
 
Using the Star Wars API (https://swapi.co/)
1. Find the ten characters who appear in the most Star Wars films
2. Sort those ten characters by height in descending order (i.e., tallest first)
3. Produce a CSV with the following columns: name, species, height, appearances
4. Send the CSV to httpbin.org
5. Create automated tests that validate your code
 
Sample CSV output (actual results may vary):
name,species,height,appearances
Chewbacca,Wookiee,228,5
Darth Vader,Human,202,4
Obi-Wan Kenobi,Human,182,6
Han Solo,Human,180,4
Luke Skywalker,Human,172,5
Palpatine,Human,170,5
C-3PO,Droid,167,6
Leia Organa,Human,150,5
R2-D2,Droid,96,7
Yoda,Yoda's species,66,5
    
# How to run (Docker base)

Requirements
-------------

- Docker

1.- Build docker image

`docker build -t star_wars_etl Dockerfile .`

2.- Run docker image

`docker run -v "$(pwd)"/output/:/src/output star_wars_etl`

This will generate the output.csv file inside a mounted volume called `output` in your current directory

2.- Run tests

`docker run -it --entrypoint=tox star_wars_etl`