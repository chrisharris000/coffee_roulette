# Coffee Roulette Project
Creating an implementation of coffee roulette, similar to [Coffee Roulette](https://coffee-roulette.com/)

## Features include:
- [ ] ~~Read list of participants from Google Form~~
- [x] Read list of participants from csv file
- [x] Create all possible pairs, taking into account an odd number of participants
- [x] Generate the current set of pairs, taking into account previous matchings
- [x] Output sets of pairs (csv)
- [x] Output sets of pairs (md)
- [ ] Create Flask application to display weekly pairs
- [ ] Add additional info to website such as cafe suggestions and conversation starters

## Usage
1. `$ git clone https://github.com/chrisharris000/coffee_roulette/tree/master`
2. `$ cd coffee_roulette`
3. `$ git checkout stable`
4. `$ pip install -r requirements.txt`
5. Convert Google Form responses to Google Sheets
6. Download Google Sheets responses as a .csv file (File -> Download -> Comma Separated Values) into the same directory as the `roulette.py` program
7. Change relevant values of `config.yaml`
   - **participant_file:** the name of the csv file you downloaded
   - **name_column_index:** the column number that the participants name is in, zero-indexed (e.g. A is 0, B is 1)
   - **email_column_index:** the column number that the participants email is in, zero-indexed
   - **team_column_index:** the column number that the participants team is in, zero-indexed
   - **year_column_index:** the column number that the participants year is in, zero-indexed
   - **pairs_csv_file:** the name of the output file for the pairs (csv format)
   - **pairs_md_file:** the name of the output file for the pairs (md format, useful for posting on Slack)
8. `$ python roulette.py`
9. The generated pairs will be available in the terminal, .csv file and .md files
