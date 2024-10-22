import random
import pandas as pd

# reading in subteam members and teams
xlsx = pd.read_excel('CU_GeoData_FA24.xlsx', header=0)
# dict: name: subteam
people = dict(zip(xlsx['Name'], xlsx['Subteam']))

def pick_people_weekly_bonus(people_name, num_people_per_week, num_weeks):
    weekly_selected_people = {}
    
    for week in range(1, num_weeks + 1):  # Loop through each week
        selected_people = random.sample(people_name, num_people_per_week)  # Randomly select people
        weekly_selected_people[f'selected_people_week_{week}'] = selected_people  # Store in dictionary
        
        # Remove the selected people from the pool for the next week
        people_name = [person for person in people_name if person not in selected_people]
    
    return weekly_selected_people

people_name = list(people.keys())
num_people_per_week = len(people_name) // 5

# Listing selected people each week 
selected_people_per_week = pick_people_weekly_bonus(people_name, num_people_per_week, 5)
for var_name, var_value in selected_people_per_week.items():
    print(f"{var_name}: {var_value}")

# Initialize a dictionary to store dataframes for each subteam
subteam_data = {subteam: pd.DataFrame(columns=['Sniper', 'Sniped', 'Points']) for subteam in list(people.values())}
print(subteam_data)

# Function to update points and record the sniping event in the appropriate DataFrame
def update_points(sniper, sniped, selected_people, subteam_points, people, subteam_data, bonus_points=2, regular_points=1):
    sniper_team = people[sniper]
    sniped_team = people[sniped]
    
    # No points if the sniper and sniped are from the same subteam
    if sniper_team == sniped_team:
        points_awarded = 0
       
    # If the sniped person is in the selected group, sniper's subteam gets bonus points
    elif sniped in selected_people:
        points_awarded = bonus_points
        subteam_points[sniper_team] += bonus_points
       
    else:
        points_awarded = regular_points
        subteam_points[sniper_team] += regular_points
    
    # Record the sniping event in the corresponding subteam's DataFrame
    new_row = {'Sniper': sniper, 'Sniped': sniped, 'Points': points_awarded}
    subteam_data[sniper_team] = subteam_data[sniper_team]._append(new_row, ignore_index=True)

# Dictionary to keep track of points of each subteam
subteam_points = {subteam: 0 for subteam in set(people.values())}

# Initialize a dictionary to store dataframes for each subteam
subteam_data = {subteam: pd.DataFrame(columns=['Sniper', 'Sniped', 'Points']) for subteam in subteam_points}

# Sample sniper/sniped data
selected_people = ['Melinda Lin', 'William Leung']  
update_points('Victoria Liu', 'Melinda Lin', selected_people, subteam_points, people, subteam_data)  
update_points('Jack Halberstadt', 'Uma Grover', selected_people, subteam_points, people, subteam_data)  
update_points('Kevin Shang', 'William Leung', selected_people, subteam_points, people, subteam_data)  
update_points('Melinda Lin', 'Helena Donnelly', selected_people, subteam_points, people, subteam_data)  # Same subteam

# Show the sniping data for all subteams
for subteam, df in subteam_data.items():
    print(f"\nSniping Data for {subteam} Subteam:")
    print(df)

# Show the final points for each subteam
print("\nFinal Subteam Points:")
for subteam, points in subteam_points.items():
    print(f"{subteam}: {points} points")