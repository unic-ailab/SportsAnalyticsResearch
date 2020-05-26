# IMPORTANT NOTE for running the program:
# Please download the files "basketball-player-data.csv" and "basketball-table-data.csv" 
# from here: https://github.com/unic-ailab/SportsAnalyticsResearch/tree/master/Basketball/input
# Then, create a folder called "input" which should be located in the same folder 
# that you are running this program ("NBAAnalyzer.py") from, and move the two downloaded files into that folder
# Also, the program will create an "output" directory by itself after being executed and 
 #it will contain two files with results (one extended, and one truncated)

import csv
import numpy as np
from numpy import genfromtxt
import sys
from pathlib import Path

base_path = Path(__file__).parent # path to the directory that this program is being run from
weighted_minutes_mode = 1 # 0 = average of player ratings without considering minutes, 1 = weighted average of player ratings with minutes taken into account
minutes_threshold = 500 # the minimum minutes a player must have played in a specific season for a specific team to be considered for analysis

# This provided input file contains the fields: UID, player, team, minutes played, PER, season for all NBA players between regular seasons 09/10 and 18/19
input_file_path = (base_path / "input/basketball-player-data.csv").resolve()
alldata_unfiltered = genfromtxt(input_file_path, delimiter=',', encoding='utf-8', dtype=str)
cols = alldata_unfiltered[0].size # column names: (0 = UID, 1 = name, 2 = team, 3 = minutes played, 4 = PER (Player Efficiency Rating), 5 = season)
alldata_unfiltered = np.delete(alldata_unfiltered,(0),axis = 0) # remove the first row (column names)
rows = int(alldata_unfiltered.size / cols) # each row corresponds to a player's entry in a season with a specific team
np.set_printoptions(threshold=sys.maxsize) # print whole array when printing the array

# detect all seasons
# detect teams in the NBA of each season
# keep track of their players in the current season (e.g. 18-19)
# find the ratings of those players in the previous season (i.e. 17-18)

alldata = []
excluded_players = []
# REMOVE entries which do not meet minute threshold
# but keep track of them to see how many players were excluded per team

for row_num in range(rows):
        if(int(alldata_unfiltered[row_num][3]) >= minutes_threshold):
            alldata.append([alldata_unfiltered[row_num][0],alldata_unfiltered[row_num][1],alldata_unfiltered[row_num][2],alldata_unfiltered[row_num][3],alldata_unfiltered[row_num][4],alldata_unfiltered[row_num][5]])
        else:
            excluded_players.append([alldata_unfiltered[row_num][0],alldata_unfiltered[row_num][1],alldata_unfiltered[row_num][2],alldata_unfiltered[row_num][3],alldata_unfiltered[row_num][4],alldata_unfiltered[row_num][5]])

cols = len(alldata[0])
rows = len(alldata)

# detect all seasons and the teams in each season
seasons_teams_temp = []
for row_num in range(rows):
    seasons_teams_temp.append([alldata[row_num][5],alldata[row_num][2],0,0,0,0,0,0])
    # 0s correspond to total players, total ratings, average ratings (which are calculated later on), actual position in that season, ratings position in that season, total mins played by players in that season

# remove the duplicates so that teams do not show up multiple times per season
seasons_teams = []
for x in seasons_teams_temp:
    if x not in seasons_teams:
        seasons_teams.append(x)

seasons_teams.sort()
# seasons_teams fields: season, team

# keep track of the players that played for each team in a given season (except the first season since there is no previous data)
# give them a 'previous season rating' of -1 (to detect the missing players i.e. ones that didn't play in the season prior in order to remove them) and then overwrite that when actually checking for their previous rating
player_data_temp = []
missing_players = []
for row_num in range(len(seasons_teams)):
    for row_num_new in range(rows):
        if(seasons_teams[row_num][0] != "09-10"):
            if(alldata[row_num_new][2] == seasons_teams[row_num][1] and alldata[row_num_new][5] == seasons_teams[row_num][0]):
                # get the string with the season, separate it, subtract 1 from each side, put it back together, add the result as a new field (previous season)
                # special case - the season before 00-01 was 99-00
                current_season_split = seasons_teams[row_num][0].split("-")
                if(int(current_season_split[0]) == '00'):
                    y1 = 99;
                else:
                    y1 = int(current_season_split[0])-1

                # if between 01 and 09, add a leading 0 to the start so it follows the format used for seasons (XX-YY), i.e. 9-10 becomes 09-10
                if(y1 >= 1 and y1 <= 9):
                    y1 = str("0")+str(y1)

                # special case - the season before 99-00 was 98-99
                if(int(current_season_split[1]) == '00'):
                    y2 = 99;
                else:
                    y2 = int(current_season_split[1])-1

                # if between 01 and 09, add a leading 0 to the start so it follows the format used for seasons (XX-YY), i.e. 9-10 becomes 09-10
                if (y2 >= 1 and y2 <= 9):
                    y2 = str("0") + str(y2)

                season = seasons_teams[row_num][0]
                team = seasons_teams[row_num][1]
                prev_season = str(y1)+"-"+str(y2)
                prev_rating = float(-1) # # players with a rating of -1 are then removed because they are the missing players; non-missing players have their rating updated
                found = 0
                minutes = int(alldata[row_num_new][3])
                player = alldata[row_num_new][0] # player's UID
                player_name = alldata[row_num_new][1]

                # for weighted average
                prev_rating1 = float(-1)
                prev_rating2 = 0
                prev_rating3 = 0
                prev_mins1 = 0
                prev_mins2 = 0
                prev_mins3 = 0
                total_mins = 0
                current_total_mins = 0
                weighted_rating = float(-1)

                if weighted_minutes_mode == 0:
                # find player's rating from previous season
                    for x in range(rows):
                        if(alldata[x][0] == player and alldata[x][5] == prev_season):
                            found+=1
                            if(found==1):
                                prev_rating = float(alldata[x][4])
                            # if the player played for more than 1 team in a season, take their average rating from that season
                            if(found>1):
                                prev_rating += float(alldata[x][4])
                                prev_rating = prev_rating/found

                    if(prev_rating != -1):
                        player_data_temp.append([season,team,player,prev_season,prev_rating,found])

                    else:
                        missing_players.append([season, team, player, prev_season, prev_rating, found])

                else:
                    # find player's rating from previous season
                    for x in range(rows):
                        if (alldata[x][0] == player and alldata[x][5] == prev_season):
                            found += 1
                            minutes = float(alldata[x][3])
                            if (found == 1):
                                prev_rating1 = float(alldata[x][4])
                                prev_mins1 = float(alldata[x][3])
                                total_mins = prev_mins1
                                weighted_rating = prev_rating1

                            # if the player played for more than 1 team in a season, take their minute-weighted average rating from that season
                            if (found == 2):
                                prev_rating2 = float(alldata[x][4])
                                prev_mins2 = float(alldata[x][3])
                                total_mins = prev_mins1 + prev_mins2
                                weighted_rating = (prev_rating1 * (prev_mins1/total_mins)) + (prev_rating2 * (prev_mins2/total_mins))

                            if(found == 3):
                                prev_rating3 = float(alldata[x][4])
                                prev_mins3 = float(alldata[x][3])
                                total_mins = prev_mins1 + prev_mins2 + prev_mins3
                                weighted_rating = (prev_rating1 * (prev_mins1/total_mins)) + (prev_rating2 * (prev_mins2/total_mins)) + (prev_rating3 * (prev_mins3/total_mins))

                        if (alldata[x][0] == player and alldata[x][5] == season and alldata[x][2] == team):
                            current_total_mins = float(alldata[x][3])
                            # finding that player's minutes played in the current season for a specific team, used for weighting ratings later on

                    if(weighted_rating != -1):
                        player_data_temp.append([season, team, player, prev_season, weighted_rating, found, total_mins, current_total_mins])

                    else:
                        missing_players.append([season, team, player, prev_season, weighted_rating, found, total_mins, current_total_mins])

# array including the talent ratings of players for each season
talent_ratings_per_season = np.array([],dtype='f')

# find the top 15% percentile value for talent for each season
seasons_talent_thresholds = []
first_season_start = 10 # first season we are looking for talent in is 10/11
for x in range(9):
    for y in range(len(player_data_temp)):
        if(str(player_data_temp[y][0])) == str(first_season_start)+str("-")+str(first_season_start+1): # if player is found in that specific season, add their rating to the rating array so that the percentile can be calculated
            talent_ratings_per_season = np.append(talent_ratings_per_season,player_data_temp[y][4])

    # find the top 15% percentile
    seasons_talent_thresholds.append([str(first_season_start)+str("-")+str(first_season_start+1),np.percentile(talent_ratings_per_season,85)])
    talent_ratings_per_season = np.array([],dtype='f') # clear the talent rating array so that it can be populated with data from the next season
    first_season_start += 1

# identify the elite talents (the players whose talent ratings in a given season are equal to or higher than the top 15% percentile value for talent in each season)
# also identify the non-elite talents
elite_talents = []
non_elite_talents = []
for x in range(len(player_data_temp)):
    current_season = player_data_temp[x][0] # find the season that the player entry corresponds to

    # find the talent threshold for that season
    for y in range(9):
        if(current_season == seasons_talent_thresholds[y][0]):
            current_season_talent_threshold = seasons_talent_thresholds[y][1]
            if(player_data_temp[x][4] >= current_season_talent_threshold):
                elite_talents.append([player_data_temp[x][0],player_data_temp[x][1],player_data_temp[x][2],player_data_temp[x][4]]) # copy season, team, player, rating
            else:
                non_elite_talents.append([player_data_temp[x][0],player_data_temp[x][1],player_data_temp[x][2],player_data_temp[x][4]]) # copy season, team, player, rating

collective_elite_talent_per_team = []
collective_non_elite_talent_per_team = []
# calculate the collective PER of all the elites of each team to use as a tiebreaker
for x in range(len(seasons_teams)):
    # copy season, team, and third field is 0 (placeholder for top talent)
    if(seasons_teams[x][0] != "09-10"):
        season_now = seasons_teams[x][0]
        team_now = seasons_teams[x][1]
        team_previous = seasons_teams[x-1][1] # note that we don't have to worry about x = 0 because that's an entry attached to 09/10 which is excluded

        elite_collective_talent = 0
        nonelite_collective_talent = 0

        for y in range(len(elite_talents)):
            if(season_now == elite_talents[y][0] and team_now == elite_talents[y][1]):
                elite_collective_talent += elite_talents[y][3]

        for z in range(len(non_elite_talents)):
            if(season_now == non_elite_talents[z][0] and team_now == non_elite_talents[z][1]):
                nonelite_collective_talent += non_elite_talents[z][3]

        collective_elite_talent_per_team.append([season_now, team_now, elite_collective_talent])
        collective_non_elite_talent_per_team.append([season_now, team_now, nonelite_collective_talent])

# calculate how many elite talents and non-elite players each team had in each season
# also keep track of the uncategorized players i.e. players who played more than or equal to the minute threshold this season, but not last season (e.g. new players to the league)
# also keep track of the excluded players i.e. players who played less than the minute threshold this season
team_elite_talents = []
team_non_elite_talents = []
for x in range(30,len(seasons_teams)): # start from season 10/11, ignoring 09/10 since no talent ratings were calculated for then
    season = seasons_teams[x][0]
    team = seasons_teams[x][1]
    elite_count = 0 # number of elite players
    non_elite_count = 0
    missing_count = 0
    excluded_count = 0
    for y in range(len(elite_talents)):
        if(season == elite_talents[y][0] and team == elite_talents[y][1]):
            elite_count += 1
    for z in range(len(non_elite_talents)):
        if(season == non_elite_talents[z][0] and team == non_elite_talents[z][1]):
            non_elite_count += 1
    for a in range(len(missing_players)):
        if(season == missing_players[a][0] and team == missing_players[a][1]):
            missing_count += 1
    for b in range(len(excluded_players)):
        if(season == excluded_players[b][5] and team == excluded_players[b][2]):
            excluded_count += 1

    team_elite_talents.append([season, team, elite_count, non_elite_count, missing_count, excluded_count])

# this provided input file contains the fields: season, rank, team for all NBA teams between regular seasons 10/11 and 18/19
input_file_path = (base_path / "input/basketball-table-data.csv").resolve()
nbatables = genfromtxt(input_file_path, delimiter=',', encoding='utf-8', dtype=str)
nbacols = nbatables[0].size # column names: (0 = season, 1 = position, 2 = team)
nbatables = np.delete(nbatables,(0),axis = 0) # remove the first row (column names)
nbarows = int(nbatables.size / nbacols) # each row corresponds to a team's position and points in a season

# add number of elite talents as a field to new array
nbatables_with_elites = []
for x in range(nbarows):
    season = nbatables[x][0]
    league_pos = nbatables[x][1]
    team = nbatables[x][2]

    for y in range(len(team_elite_talents)):
        if(season == team_elite_talents[y][0] and team == team_elite_talents[y][1]):
            num_elites = team_elite_talents[y][2]
            num_nonelites = team_elite_talents[y][3]
            num_missing = team_elite_talents[y][4]
            num_excluded = team_elite_talents[y][5]
            talent_pos = 0 # to be calculated

            collective_talents_of_elites = 0
            for a in range(len(collective_elite_talent_per_team)):
                if (season == collective_elite_talent_per_team[a][0] and team == collective_elite_talent_per_team[a][1]):
                    collective_talents_of_elites += collective_elite_talent_per_team[a][2]

            collective_talents_of_nonelites = 0
            for b in range(len(collective_non_elite_talent_per_team)):
                if (season == collective_non_elite_talent_per_team[b][0] and team == collective_non_elite_talent_per_team[b][1]):
                    collective_talents_of_nonelites += collective_non_elite_talent_per_team[b][2]

            nbatables_with_elites.append([season,team,league_pos,num_elites,num_nonelites,num_missing,num_excluded,talent_pos,collective_talents_of_elites,collective_talents_of_nonelites])


nbatables_with_elites_sorted = sorted(nbatables_with_elites,key=lambda x: (x[0],-x[3],-x[8], x[5], -x[9]))
# sort by season, and then number of elite talents (descending), and then team with higher collective elite talent (descending),
# and then team with less missing players (ascending), then team with higher collective non-elite talent (descending)

# the following code assigns talent positions to each team in each season
# it also accounts for ties:
# if many teams have the same number of elite talents, precedence is given to the team which has higher collective elite talent
# if many teams have the same number of collective elite talent, precedence is given to the team which has less missing players
# if many teams have the same number of missing players, precedence is given to the team which has higher collective non-elite talent

rank = 1
for x in range(len(nbatables_with_elites)):
    current_elites = nbatables_with_elites_sorted[x][3] # number of elites of current team
    current_elites_season = nbatables_with_elites_sorted[x][0] # current season, so as to know when to start ranking again from the next season
    current_missing = nbatables_with_elites_sorted[x][5]
    current_collective_elite_talent = nbatables_with_elites_sorted[x][8]
    current_collective_nonelite_talent = nbatables_with_elites_sorted[x][9]

    # special case
    # first team to be ranked
    if(x == 0):
        nbatables_with_elites_sorted[x][7] = 1 # first team to be ranked is always 1st

    if(x > 0):
        previous_elites_season = nbatables_with_elites_sorted[x-1][0]
        previous_elites = nbatables_with_elites_sorted[x-1][3] # number of elites of previous team
        previous_rank = nbatables_with_elites_sorted[x-1][7]
        previous_missing = nbatables_with_elites_sorted[x-1][5]
        previous_collective_elite_talent = nbatables_with_elites_sorted[x-1][8]
        previous_collective_nonelite_talent = nbatables_with_elites_sorted[x-1][9]

    if(x < len(nbatables_with_elites)-1):
        next_elites_season = nbatables_with_elites_sorted[x+1][0]

    # switching seasons
    if(x > 0 and current_elites_season != previous_elites_season):
        rank = 1
        nbatables_with_elites_sorted[x][7] = rank

    if(x > 0 and current_elites_season == previous_elites_season):
        if(current_elites < previous_elites):
            rank+=1
            nbatables_with_elites_sorted[x][7] = rank
        if(current_elites == previous_elites):
            # if many teams have the same number of elite talents, precedence is given to the team which has higher collective elite talent
            if(current_collective_elite_talent < previous_collective_elite_talent):
                rank += 1
                nbatables_with_elites_sorted[x][7] = rank
            if(current_collective_elite_talent == previous_collective_elite_talent):
                # if many teams have the same number of collective elite talent, precedence is given to the team which has less missing players
                if(current_missing > previous_missing):
                    rank += 1
                    nbatables_with_elites_sorted[x][7] = rank
                if(current_missing == previous_missing):
                    # if many teams have the same number of missing players, precedence is given to the team with highest collective non-elite talent
                    if(current_collective_nonelite_talent < previous_collective_nonelite_talent):
                        rank += 1
                        nbatables_with_elites_sorted[x][7] = rank
                    if(current_collective_nonelite_talent == previous_collective_nonelite_talent):
                        nbatables_with_elites_sorted[x][7] = previous_rank
                        rank += 1


# output array to file (extended data)
output_file_path = (base_path / "output/basketball-extended-results.csv").resolve()

with open(output_file_path, 'w') as f:
    print("season,team,league_position,elites,non-elites,missing,excluded,talent_position,elite_collective_talent,non-elite_collective_talent",file=f)
    for x in range(len(nbatables_with_elites)):
        print("\'" + nbatables_with_elites_sorted[x][0] + "\'", nbatables_with_elites_sorted[x][1], str(nbatables_with_elites_sorted[x][2]), str(nbatables_with_elites_sorted[x][3]),
              str(nbatables_with_elites_sorted[x][4]), str(nbatables_with_elites_sorted[x][5]), str(nbatables_with_elites_sorted[x][6]),
              str(nbatables_with_elites_sorted[x][7]), str(nbatables_with_elites_sorted[x][8]), str(nbatables_with_elites_sorted[x][9]), sep=",",file=f)

# output array to file (truncated data)
output_file_path = (base_path / "output/basketball-truncated-results.csv").resolve()

with open(output_file_path, 'w') as f:
    print("season,team,elites,league_position,talent_position",file=f)
    for x in range(len(nbatables_with_elites)):
        print("\'" + nbatables_with_elites_sorted[x][0] + "\'", nbatables_with_elites_sorted[x][1], nbatables_with_elites_sorted[x][3], nbatables_with_elites_sorted[x][2], nbatables_with_elites_sorted[x][7], sep=",",file=f)

# print correlation of league pos + talent pos
talent_positions = np.array([])
league_positions = np.array([])

for x in range(len(nbatables_with_elites)):
    talent_positions = np.append(int(nbatables_with_elites_sorted[x][7]),talent_positions)
    league_positions = np.append(int(nbatables_with_elites_sorted[x][2]),league_positions)

print("Pearson Correlation Coefficient between Talent Position and League Position [BASKETBALL]: ")
print(np.corrcoef(talent_positions.astype(int),league_positions.astype(int))[0][1])
