import pandas as pd
import re

def get_basic_stats(games, player_stats):
    
    def extract_game_stats(game_df, player_stats, mode_key):
        stats = {}

        stats["white"] = {
            
            "win": len(game_df[(game_df['player_color'] == 'white') & (game_df['result'].str.contains('win'))]),
            "loss": len(game_df[(game_df['player_color'] == 'white') & (game_df['result'].str.contains('loss'))]),
            "draw": len(game_df[(game_df['player_color'] == 'white') & (game_df['result'].str.contains('draw'))]),
        }

        stats["black"] = {
            "win": len(game_df[(game_df['player_color'] == 'black') & (game_df['result'].str.contains('win'))]),
            "loss": len(game_df[(game_df['player_color'] == 'black') & (game_df['result'].str.contains('loss'))]),
            "draw": len(game_df[(game_df['player_color'] == 'black') & (game_df['result'].str.contains('draw'))]),
        }
        stats["white"]["total"] = stats["white"]["win"] + stats["white"]["loss"] + stats["white"]["draw"]
        stats["black"]["total"] = stats["black"]["win"] + stats["black"]["loss"] + stats["black"]["draw"]
        
        stats["current"] = {
            "rating": player_stats[f'chess_{mode_key}']['last']['rating'],
            "date": player_stats[f'chess_{mode_key}']['last']['date'],
        }

        
        best_data = player_stats.get(f'chess_{mode_key}', {}).get('best', {})
        if not game_df.empty:
            stats["best"] = {
                "rating": game_df['player_rating'].max(),
                "date": game_df.loc[game_df['player_rating'].idxmax(), 'end_time']
            }
        else:
            stats['best'] = None

        if not game_df.empty:
            stats["first_game"] = {
                "rating": game_df.iloc[-1]['player_rating'],
                "date": game_df.iloc[-1]['end_time'],
                "game": game_df.iloc[-1]['url']
            }
        else:
            stats["first_game"] = None

        if not game_df.empty:
            stats["latest_game"] = {
                "rating": game_df.iloc[0]['player_rating'],
                "date": game_df.iloc[0]['end_time'],
                "game": game_df.iloc[0]['url']
            }
        else:
            stats["first_game"] = None


        rated_wins = game_df[(game_df['result'].str.contains('win')) & (game_df['rated'] == True)]
        if not rated_wins.empty:
            best_idx = rated_wins['opponent_rating'].idxmax()
            stats["best_game"] = {
                "rating": game_df.loc[best_idx, 'player_rating'],
                "date": game_df.loc[best_idx, 'end_time'],
                "game": game_df.loc[best_idx, 'url']
            }
        else:
            stats["best_game"] = None

        stats['loss_reason'] = game_df['result'][game_df['result'].str.contains('loss_by')].value_counts().head(3).to_dict()
        return stats
    res = {
        'all_time_tactics_best': player_stats.get('tactics', {}).get('highest', {}),
        'all_time_puzzle_rush': player_stats.get('puzzle_rush', {})
    }

    for mode in ['rapid', 'blitz', 'bullet', 'daily']:
        if mode in games and f'chess_{mode}' in player_stats:
            res[mode] = extract_game_stats(games[mode], player_stats, mode)

    return res

def get_opening_stats(games, mode_key):
    stats = {}
    game_df = games[mode_key]
    
    if game_df.empty:
        stats["top_openings"] = {
            "white": [],
            "black": [],
            "most_common_win_openings": [],
            "most_common_loss_openings": [],
            "most_common_draw_openings": []
        }
        return stats
    
    def summarize_openings(df):
        opening_stats = {}
        grouped = df.groupby('eco_url')

        for eco_url, group in grouped:
            name = group['eco_name'].iloc[0]
            total = len(group)
            win = len(group[group['result'].str.contains('win')])
            loss = len(group[group['result'].str.contains('loss')])
            draw = len(group[group['result'].str.contains('draw')])
            avg_opponent_rating = round(group['opponent_rating'].mean(), 2)

            opening_stats[eco_url] = {
                "name": name,
                "url": eco_url,
                "games": total,
                "wins": win,
                "losses": loss,
                "draws": draw,
                "win_rate": round(100 * win / total, 1) if total > 0 else 0,
                "loss_rate": round(100 * loss / total, 1) if total > 0 else 0,
                "draw_rate": round(100 * draw / total, 1) if total > 0 else 0,
                "avg_opponent_rating": avg_opponent_rating
            }
        return sorted(opening_stats.values(), key=lambda x: x['games'], reverse=True)[:5]

    def most_common_openings_for_result(result_label, color):
        sub_df = game_df[game_df['result'].str.contains(result_label) &
        (game_df['player_color'] == color)]
        
        if sub_df.empty:
            return []
    
        top_openings = sub_df['eco_url'].value_counts().head(5).index.tolist()
    
        result_entries = []
        for eco_url in top_openings:
            subset = game_df[game_df['eco_url'] == eco_url]
            total = len(subset)
            if total == 0:
                continue
            win_count = len(subset[subset['result'].str.contains('win')])
            loss_count = len(subset[subset['result'].str.contains('loss')])
            draw_count = len(subset[subset['result'].str.contains('draw')])
    
            result_entries.append({
                "eco_url": eco_url,
                "name": subset['eco_name'].iloc[0],
                "total": total,
                "win": win_count,
                "loss": loss_count,
                "draw": draw_count,
                "win_rate": round(100 * win_count / total, 1),
                "loss_rate": round(100 * loss_count / total, 1),
                "draw_rate": round(100 * draw_count / total, 1),
            })
    
        return sorted(result_entries, key = lambda x: x[f'{result_label}_rate'], reverse=True)

    stats["top_openings"] = {
        "white": summarize_openings(game_df[game_df['player_color'] == 'white']),
        "black": summarize_openings(game_df[game_df['player_color'] == 'black'])
    }

    stats["most_common_win_openings"] = {
    "white": most_common_openings_for_result('win', 'white'),
    "black": most_common_openings_for_result('win', 'black')
    }
    stats["most_common_loss_openings"] = {
        "white": most_common_openings_for_result('loss', 'white'),
        "black": most_common_openings_for_result('loss', 'black')
    }
    stats["most_common_draw_openings"] = {
        "white": most_common_openings_for_result('draw', 'white'),
        "black": most_common_openings_for_result('draw', 'black')
    }
    
    return stats

def get_winloss_stats(games, mode_key):
    game_df = games[mode_key]

    if game_df.empty:
        return {"win":{}, "loss":{}, "draw":{}}

    res = {"win":{}, "loss":{}, "draw":{}}
    
    for result, count in game_df['result'].value_counts().items():
        if result.startswith('win_by_'):
            res["win"][result] = count
        elif result.startswith('loss_by_'):
            res["loss"][result] = count
        else:
            res["draw"][result] = count
    return res

def get_progress_stats(games, mode_key):
    game_df = games[mode_key]
    game_df = game_df.sort_values('end_time').reset_index(drop=True)
    
    acc_df = game_df[~game_df['player_accuracy'].isna()].reset_index(drop=True)
    
    res = {}

    res['rating_progress'] = [(game_df.loc[i,'player_rating'], game_df.loc[i,'end_time']) for i in range(0, len(game_df), max(len(game_df)//300, 1))]
    res['accuracy_progress'] = [(acc_df.loc[i,'player_accuracy'], acc_df.loc[i,'end_time']) for i in range(0, len(acc_df), max(len(acc_df)//300, 1))]
    
    total = 0
    wins = 0
    win_rate_progress = []

    for i, row in game_df.iterrows():
        total += 1
        if str(row['result']).startswith('win_by_'):
            wins += 1
        win_rate = wins / total
        win_rate_progress.append((win_rate, row['end_time']))

    step = max(len(win_rate_progress) // 300, 1)
    res['win_rate_progress'] = win_rate_progress[::step] 
    
    return res

def get_detailed_stats(games, mode_key):
    return {
        "opening": get_opening_stats(games, mode_key),
        "win_loss": get_winloss_stats(games, mode_key),
        "progression": get_progress_stats(games, mode_key)
    }