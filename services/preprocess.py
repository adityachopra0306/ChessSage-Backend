from utils.utils import dates_to_string
from datetime import datetime
import re
import pandas as pd

def preprocess_profile(profile):
    profile["last_online"] = datetime.fromtimestamp(profile["last_online"]).strftime("%Y-%m-%d")
    profile["joined"] = datetime.fromtimestamp(profile["joined"]).strftime("%Y-%m-%d")
    return profile

def preprocess_stats(stats):
    return dates_to_string(stats)

def preprocess_games(games_df, username):
    '''
    Returns a player-centric DataFrame with normalized columns, result labels, and opening names.
    '''
    def normalize_columns(df):
        white_df = pd.json_normalize(df['white'])
        black_df = pd.json_normalize(df['black'])
        acc_df = pd.json_normalize(df['accuracies'])

        white_df.columns = ['white_' + col for col in white_df.columns]
        black_df.columns = ['black_' + col for col in black_df.columns]
        acc_df.columns = [col + "_accuracy" for col in acc_df.columns]

        df = df.drop(columns=['white', 'black', 'accuracies'])
        df = pd.concat([df, white_df, black_df, acc_df], axis=1)
        return df

    def parse_eco_name(url):
        if not isinstance(url, str) or not url.startswith("https://www.chess.com/openings/"):
            return None
        try:
            name_part = url.split("https://www.chess.com/openings/")[1]
            name_part = name_part.replace('-', ' ')

            if re.search(r'\d\.', name_part):
                name, moves = re.split(r'(?=\d+\.\.\.| \d\.)', name_part, maxsplit=1)
                moves = moves.strip().replace('...', '... ').replace('-', ' ')
                formatted = f"{name.strip()} ({moves.strip()})"
            else:
                formatted = name_part.strip()
            return formatted
        except:
            return None

    def normalize_by_user(df, player_id):

        df['player_color'] = (
            df['white_@id']
            .str.rsplit('/', n=1).str[-1]
            .str.lower()
            .eq(player_id.lower())
            .map({True: 'white', False: 'black'})
        )

        def format_reason(reason):
            match reason:
                case "resigned":
                    return "resignation"
                case "checkmated":
                    return "checkmate"
                case "agreed":
                    return "agreement"
                case "abandoned":
                    return "abandonment"
                case "insufficient":
                    return "insufficient_material"
                case "timevsinsufficient":
                    return "timeout_vs_insufficient"
            return reason
            
        def get_result(row):
            white_res = format_reason(row['white_result'].lower())
            black_res = format_reason(row['black_result'].lower())
            color = row['player_color']
        
            if white_res == 'win' and black_res != 'win':
                return 'win_by_' + black_res if color == 'white' else 'loss_by_' + black_res
            elif black_res == 'win' and white_res != 'win':
                return 'win_by_' + white_res if color == 'black' else 'loss_by_' + white_res
            else:
                return 'draw_by_' + white_res

        
        is_white = df['player_color'] == 'white'

        df['player_rating'] = df['white_rating'].where(is_white, df['black_rating'])
        df['opponent_rating'] = df['black_rating'].where(is_white, df['white_rating'])

        df['player_accuracy'] = df['white_accuracy'].where(is_white, df['black_accuracy'])
        df['opponent_accuracy'] = df['black_accuracy'].where(is_white, df['white_accuracy'])

        df['opponent_username'] = df['black_username'].where(is_white, df['white_username'])
        df['opponent_@id'] = df['black_@id'].where(is_white, df['white_@id'])
        
        df['result'] = df.apply(get_result, axis=1)
        
        df = df[df['rules'] == 'chess'].copy()

        cols_to_drop = [col for col in df.columns if col.startswith('white_') or col.startswith('black_')]
        cols_to_drop.extend(['rules', 'tcn', 'uuid', 'white_uuid', 'black_uuid', 'start_time', 'tournament', 'initial_setup'])
        df.drop(columns=cols_to_drop, inplace=True, errors = 'ignore')
        return df


    games_df = normalize_columns(games_df)

    games_df['end_time'] = pd.to_datetime(games_df['end_time'], unit='s').dt.date
 
    games_df = games_df.dropna(subset=['eco'])
    games_df['eco_name'] = games_df['eco'].apply(parse_eco_name)
    games_df.rename(columns={'eco': 'eco_url'}, inplace=True)
    games_df.loc[games_df['eco_url'].str.contains('Undefined', na=False), 'eco_name'] = 'Dubious Opening'
    games_df = normalize_by_user(games_df, username)
    
    return games_df

def split_by_mode(games_df):
    modes = ['rapid', 'bullet', 'blitz', 'daily']
    return {mode: games_df[games_df['time_class'] == mode].reset_index(drop=True) for mode in modes}