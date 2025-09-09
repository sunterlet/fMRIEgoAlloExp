import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
from itertools import combinations

def detect_outliers(data, column='error_distance'):
    """Detect outliers using IQR method."""
    Q1 = data[column].quantile(0.25)
    Q3 = data[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = data[(data[column] < lower_bound) | (data[column] > upper_bound)]
    return outliers, lower_bound, upper_bound

def load_all_data():
    """Load all discrete log files and combine them into one DataFrame."""
    base_dir = Path("results_prolific")
    all_data = []
    
    # Create a mapping of original IDs to numeric IDs
    participant_ids = set()
    for csv_file in base_dir.rglob("discrete_log_*.csv"):
        participant_id = csv_file.parent.parent.name
        participant_ids.add(participant_id)
    
    # Create mapping dictionary
    id_mapping = {pid: i+1 for i, pid in enumerate(sorted(participant_ids))}
    
    # Find all discrete log files
    for csv_file in base_dir.rglob("discrete_log_*.csv"):
        try:
            df = pd.read_csv(csv_file)
            # Add numeric participant ID
            original_id = csv_file.parent.parent.name
            df['participant_id'] = id_mapping[original_id]
            all_data.append(df)
        except Exception as e:
            print(f"Error loading {csv_file}: {str(e)}")
    
    return pd.concat(all_data, ignore_index=True)

def filter_participants(df):
    """Filter participants based on data completeness and error thresholds."""
    # Add phase column
    df['phase'] = df['trial'].apply(lambda x: 'Training' if x.startswith('training') 
                                   else 'Dark Training' if x.startswith('dark_training')
                                   else 'Test')
    
    # Expected number of trials per phase
    expected_trials = {
        'Training': 3,
        'Dark Training': 3,
        'Test': 5
    }
    total_expected = sum(expected_trials.values())
    
    # Calculate completion rate for each participant
    completion_rates = []
    for participant in df['participant_id'].unique():
        participant_data = df[df['participant_id'] == participant]
        valid_trials = participant_data['error_distance'].notna().sum()
        completion_rate = valid_trials / total_expected
        completion_rates.append({'participant_id': participant, 'completion_rate': completion_rate})
    
    completion_df = pd.DataFrame(completion_rates)
    
    # Filter participants with ≥80% completion rate
    valid_participants = completion_df[completion_df['completion_rate'] >= 0.8]['participant_id']
    
    # Filter the main dataframe
    df_filtered = df[df['participant_id'].isin(valid_participants)]
    
    # Calculate mean error distance per participant
    participant_means = df_filtered.groupby('participant_id')['error_distance'].mean()
    
    # Calculate 90th percentile threshold
    threshold = participant_means.quantile(0.9)
    
    # Filter out participants with mean error distance above 90th percentile
    final_participants = participant_means[participant_means <= threshold].index
    
    # Create final filtered dataframe
    df_final = df_filtered[df_filtered['participant_id'].isin(final_participants)]
    
    # Print filtering statistics
    print("\nFiltering Statistics:")
    print("-" * 50)
    print(f"Original number of participants: {len(df['participant_id'].unique())}")
    print(f"Participants with ≥80% data: {len(valid_participants)}")
    print(f"Final number of participants (after 90th percentile filter): {len(final_participants)}")
    print(f"90th percentile error distance threshold: {threshold:.3f}")
    
    return df_final

def analyze_split_half_correlations(df):
    """Analyze split-half correlations for test phase data."""
    # Get test phase data
    test_data = df[df['phase'] == 'Test'].copy()
    
    # Get unique test trials
    trials = sorted(test_data['trial'].unique())
    n_trials = len(trials)
    
    print(f"\nSplit-Half Analysis:")
    print("-" * 50)
    print(f"Number of test trials: {n_trials}")
    
    # Create splits (2-3 trials in each half)
    splits = []
    if n_trials == 5:
        # For 5 trials, we can split into 2-3 or 3-2
        splits = [
            ([0, 1], [2, 3, 4]),  # First 2 vs last 3
            ([0, 1, 2], [3, 4]),  # First 3 vs last 2
            ([0, 2, 4], [1, 3]),  # Alternating trials
            ([0, 3, 4], [1, 2]),  # First and last vs middle
            ([1, 2, 3], [0, 4])   # Middle vs ends
        ]
    
    print(f"Number of splits: {len(splits)}")
    
    # Calculate correlations for each split
    correlations = []
    split_means = []
    
    for split1, split2 in splits:
        # Get trials for each split
        trials1 = [trials[i] for i in split1]
        trials2 = [trials[i] for i in split2]
        
        # Calculate means for each split
        means1 = test_data[test_data['trial'].isin(trials1)].groupby('participant_id')['error_distance'].mean()
        means2 = test_data[test_data['trial'].isin(trials2)].groupby('participant_id')['error_distance'].mean()
        
        # Store means for later analysis
        split_means.append((means1, means2))
        
        # Calculate correlation
        correlation = means1.corr(means2)
        correlations.append(correlation)
    
    # Calculate average correlation
    avg_correlation = np.mean(correlations)
    std_correlation = np.std(correlations)
    
    print(f"Average split-half correlation: {avg_correlation:.3f} ± {std_correlation:.3f}")
    
    # Create scatter plot for all splits
    plt.figure(figsize=(15, 15))
    
    for i, (means1, means2) in enumerate(split_means):
        plt.subplot(2, 3, i+1)
        plt.scatter(means1, means2, alpha=0.6)
        
        # Add perfect correlation line
        max_val = max(means1.max(), means2.max())
        plt.plot([0, max_val], [0, max_val], 'r--', label='Perfect correlation')
        
        # Add correlation line
        z = np.polyfit(means1, means2, 1)
        p = np.poly1d(z)
        plt.plot(means1, p(means1), "b--", 
                label=f'r={correlations[i]:.3f}')
        
        plt.title(f'Split {i+1}')
        plt.xlabel('Mean Error Distance (First Half)')
        plt.ylabel('Mean Error Distance (Second Half)')
        plt.legend()
    
    plt.suptitle('Split-Half Correlations of Test Phase Performance')
    plt.tight_layout()
    plt.savefig('split_half_correlations.png')
    plt.close()
    
    # Create histogram of correlations
    plt.figure(figsize=(10, 6))
    plt.hist(correlations, bins=10)
    plt.axvline(avg_correlation, color='r', linestyle='--', 
                label=f'Mean correlation: {avg_correlation:.3f}')
    plt.title('Distribution of Split-Half Correlations')
    plt.xlabel('Correlation Coefficient')
    plt.ylabel('Frequency')
    plt.legend()
    plt.tight_layout()
    plt.savefig('correlation_distribution.png')
    plt.close()
    
    # Print detailed correlation information
    print("\nDetailed Split-Half Correlations:")
    print("-" * 50)
    for i, (split1, split2) in enumerate(splits):
        print(f"\nSplit {i+1}:")
        print(f"First half trials: {[trials[j] for j in split1]}")
        print(f"Second half trials: {[trials[j] for j in split2]}")
        print(f"Correlation: {correlations[i]:.3f}")

def analyze_participant_variability(df):
    """Analyze correlation between mean and std of error distances per participant."""
    print("\nParticipant Variability Analysis:")
    print("-" * 50)
    
    # Calculate mean and std for each participant
    participant_stats = df.groupby('participant_id').agg({
        'error_distance': ['mean', 'std']
    }).reset_index()
    
    # Rename columns for clarity
    participant_stats.columns = ['participant_id', 'mean_error', 'std_error']
    
    # Calculate correlation
    correlation = participant_stats['mean_error'].corr(participant_stats['std_error'])
    
    print(f"Correlation between mean and std of error distances: {correlation:.3f}")
    
    # Create scatter plot
    plt.figure(figsize=(10, 8))
    plt.scatter(participant_stats['mean_error'], participant_stats['std_error'], alpha=0.6)
    
    # Add correlation line
    z = np.polyfit(participant_stats['mean_error'], participant_stats['std_error'], 1)
    p = np.poly1d(z)
    plt.plot(participant_stats['mean_error'], 
             p(participant_stats['mean_error']), 
             "r--", 
             label=f'Correlation (r={correlation:.3f})')
    
    plt.title('Relationship between Mean and Standard Deviation of Error Distances')
    plt.xlabel('Mean Error Distance')
    plt.ylabel('Standard Deviation of Error Distance')
    plt.legend()
    
    # Add text with statistics
    stats_text = f"Correlation: {correlation:.3f}\n"
    stats_text += f"Mean of means: {participant_stats['mean_error'].mean():.3f}\n"
    stats_text += f"Mean of STDs: {participant_stats['std_error'].mean():.3f}"
    plt.text(0.05, 0.95, stats_text,
             transform=plt.gca().transAxes,
             verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig('mean_std_correlation.png')
    plt.close()
    
    # Also analyze by phase
    print("\nBy Phase:")
    for phase in ['Training', 'Dark Training', 'Test']:
        phase_data = df[df['phase'] == phase]
        phase_stats = phase_data.groupby('participant_id').agg({
            'error_distance': ['mean', 'std']
        }).reset_index()
        phase_stats.columns = ['participant_id', 'mean_error', 'std_error']
        
        # Remove any NaN values that might occur from insufficient data
        phase_stats = phase_stats.dropna()
        
        if len(phase_stats) > 0:
            correlation = phase_stats['mean_error'].corr(phase_stats['std_error'])
            print(f"\n{phase}:")
            print(f"Correlation: {correlation:.3f}")
            print(f"Number of participants: {len(phase_stats)}")
            print(f"Mean of means: {phase_stats['mean_error'].mean():.3f}")
            print(f"Mean of STDs: {phase_stats['std_error'].mean():.3f}")
            
            # Create scatter plot for each phase
            plt.figure(figsize=(10, 8))
            plt.scatter(phase_stats['mean_error'], phase_stats['std_error'], alpha=0.6)
            
            # Add correlation line
            z = np.polyfit(phase_stats['mean_error'], phase_stats['std_error'], 1)
            p = np.poly1d(z)
            plt.plot(phase_stats['mean_error'], 
                     p(phase_stats['mean_error']), 
                     "r--", 
                     label=f'Correlation (r={correlation:.3f})')
            
            plt.title(f'Mean vs STD of Error Distances - {phase} Phase')
            plt.xlabel('Mean Error Distance')
            plt.ylabel('Standard Deviation of Error Distance')
            plt.legend()
            
            # Add text with statistics
            stats_text = f"Correlation: {correlation:.3f}\n"
            stats_text += f"Mean of means: {phase_stats['mean_error'].mean():.3f}\n"
            stats_text += f"Mean of STDs: {phase_stats['std_error'].mean():.3f}"
            plt.text(0.05, 0.95, stats_text,
                     transform=plt.gca().transAxes,
                     verticalalignment='top',
                     bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
            
            plt.tight_layout()
            plt.savefig(f'mean_std_correlation_{phase.lower().replace(" ", "_")}.png')
            plt.close()

def analyze_error_distances():
    """Analyze and visualize error distances across experiment phases."""
    # Load and filter data
    df = load_all_data()
    df = filter_participants(df)
    
    # Analyze participant variability
    analyze_participant_variability(df)
    
    # Perform split-half correlation analysis
    analyze_split_half_correlations(df)
    
    # Create figure with subplots for overall distributions
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 15))
    
    # Plot histograms for each phase
    phases = {
        'Training': df[df['phase'] == 'Training'],
        'Dark Training': df[df['phase'] == 'Dark Training'],
        'Test': df[df['phase'] == 'Test']
    }
    
    # Analyze outliers for each phase
    print("\nOutlier Analysis (After Filtering):")
    print("-" * 50)
    
    for i, (phase, data) in enumerate(phases.items()):
        # Calculate statistics
        mean_error = data['error_distance'].mean()
        std_error = data['error_distance'].std()
        median_error = data['error_distance'].median()
        
        # Detect outliers
        outliers, lower_bound, upper_bound = detect_outliers(data)
        
        # Print outlier statistics
        print(f"\n{phase} Phase:")
        print(f"Number of trials: {len(data)}")
        print(f"Mean error distance: {mean_error:.3f}")
        print(f"Standard deviation: {std_error:.3f}")
        print(f"Median error distance: {median_error:.3f}")
        print(f"Number of outliers: {len(outliers)}")
        print(f"Lower bound: {lower_bound:.3f}")
        print(f"Upper bound: {upper_bound:.3f}")
        
        # Create histogram
        if phase == 'Training':
            ax = ax1
        elif phase == 'Dark Training':
            ax = ax2
        else:
            ax = ax3
            
        sns.histplot(data=data, x='error_distance', ax=ax, bins=30)
        ax.set_title(f'{phase} Phase\nMean: {mean_error:.2f}, Std: {std_error:.2f}, Median: {median_error:.2f}')
        ax.set_xlabel('Error Distance')
        ax.set_ylabel('Count')
        
        # Add vertical lines for mean, median, and outlier bounds
        ax.axvline(mean_error, color='red', linestyle='--', label='Mean')
        ax.axvline(median_error, color='green', linestyle='--', label='Median')
        ax.axvline(lower_bound, color='orange', linestyle=':', label='Outlier Bounds')
        ax.axvline(upper_bound, color='orange', linestyle=':')
        ax.legend()
    
    plt.tight_layout()
    plt.savefig('error_distance_analysis_filtered.png')
    plt.close()
    
    # Create box plots for outlier visualization
    plt.figure(figsize=(15, 6))
    sns.boxplot(data=df, x='phase', y='error_distance')
    plt.title('Error Distance Distribution (Filtered Data)')
    plt.xlabel('Phase')
    plt.ylabel('Error Distance')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('outlier_analysis_filtered.png')
    plt.close()
    
    # Create box plots for each phase
    plt.figure(figsize=(15, 6))
    sns.boxplot(data=df, x='participant_id', y='error_distance', hue='phase')
    plt.xticks(rotation=45)
    plt.title('Error Distance Distribution by Participant and Phase (Filtered Data)')
    plt.xlabel('Participant ID')
    plt.ylabel('Error Distance')
    plt.tight_layout()
    plt.savefig('participant_performance_filtered.png')
    plt.close()
    
    # Create line plot showing mean performance across phases for each participant
    participant_means = df.groupby(['participant_id', 'phase'])['error_distance'].mean().reset_index()
    plt.figure(figsize=(15, 6))
    sns.lineplot(data=participant_means, x='phase', y='error_distance', 
                hue='participant_id', marker='o')
    plt.title('Mean Error Distance Across Phases by Participant (Filtered Data)')
    plt.xlabel('Phase')
    plt.ylabel('Mean Error Distance')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title='Participant ID')
    plt.tight_layout()
    plt.savefig('participant_progression_filtered.png')
    plt.close()

if __name__ == "__main__":
    analyze_error_distances() 