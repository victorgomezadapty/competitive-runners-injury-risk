"""Timelines on real relative-day spacing; unobserved days remain gaps."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

COLORS = {'blue': '#21618c', 'orange': '#df8b26', 'red': '#bd3d44', 'green': '#2c8a75'}


def plot_athlete(training, events, athlete, path, center=None):
    d = training[training['Athlete ID'].eq(athlete)].set_index('training_day').sort_index()
    e = events[events['Athlete ID'].eq(athlete)].sort_values('Date')
    if center is None:
        center = int(e.loc[e.injury.eq(1), 'Date'].median()) if e.injury.any() else int(e.Date.median())
    lo, hi = max(int(d.index.min()), center-70), min(int(e.Date.max()), center+35)
    d = d.reindex(range(lo, hi+1))
    x = d.index.to_numpy()
    fig, axs = plt.subplots(5, 1, figsize=(13, 10), sharex=True, layout='constrained',
                            gridspec_kw={'height_ratios': [2, 1.5, 1.5, 1.1, 1]})
    fig.suptitle(f'Athlete {athlete} | retrospective training history and retained events', fontsize=15)
    axs[0].bar(x, d['total km'], color=COLORS['blue'], width=.8)
    axs[0].set_ylabel('Running\nkm/day')
    for col, color, label in [('km Z3-4', COLORS['orange'], 'Z3-4'), ('km Z5-T1-T2', COLORS['red'], 'Z5/T1/T2'),
                               ('km sprinting', COLORS['green'], 'Sprinting')]:
        axs[1].plot(x, d[col], label=label, color=color, linewidth=1)
    axs[1].set_ylabel('Intensity\nkm/day')
    axs[1].legend(loc='upper right', ncol=3, fontsize=8)
    for col, color, label in [('perceived recovery', COLORS['green'], 'Recovery'),
                               ('perceived exertion', COLORS['red'], 'Exertion'),
                               ('perceived trainingSuccess', COLORS['blue'], 'Success')]:
        axs[2].plot(x, d[col].replace(-.01, np.nan), '.-', label=label, color=color, markersize=2, linewidth=.9)
    axs[2].set_ylabel('Released\nrating (0-1)')
    axs[2].legend(loc='upper right', ncol=3, fontsize=8)
    rest = d['nr. sessions'].eq(0)
    axs[3].scatter(x[rest], np.zeros(rest.sum()), marker='s', s=14, color=COLORS['green'], label='Zero-session day')
    axs[3].plot(x, d['hours alternative'], color=COLORS['orange'], label='Cross training (h)')
    axs[3].plot(x, d['strength training'], color=COLORS['blue'], label='Strength sessions')
    axs[3].set_ylabel('Rest / other\ntraining')
    axs[3].legend(loc='upper right', ncol=3, fontsize=8)
    selected = e[e.Date.between(lo, hi)]
    axs[4].scatter(selected.Date, np.zeros(len(selected)), s=5, color='#9aadb9', label='Selected event row')
    injuries = selected[selected.injury.eq(1)]
    axs[4].scatter(injuries.Date, np.ones(len(injuries)), marker='v', color=COLORS['red'], s=45, label='Retained injury flag')
    axs[4].set_yticks([0, 1], ['Selected', 'Injury'])
    axs[4].set_ylim(-.4, 2)
    axs[4].legend(loc='upper right', ncol=2, fontsize=8)
    axs[4].set_xlabel('Relative day index (calendar origin unavailable); blank history is not rest')
    for ax in axs:
        ax.set_xlim(lo-1, hi+1)
        for date in injuries.Date:
            ax.axvline(date, color=COLORS['red'], alpha=.4, linewidth=.8)
        ax.grid(axis='y', alpha=.15)
        ax.spines[['top', 'right']].set_visible(False)
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_event_profiles(history, path):
    variables = ['total km', 'km Z3-4', 'km Z5-T1-T2', 'perceived recovery', 'perceived exertion', 'perceived trainingSuccess']
    fig, axs = plt.subplots(2, 3, figsize=(13, 7), layout='constrained')
    fig.suptitle('Seven days before retained events | equal weight per athlete within label', fontsize=14)
    for ax, variable in zip(axs.flat, variables):
        temp = history.copy()
        if variable.startswith('perceived'):
            temp[variable] = temp[variable].replace(-.01, np.nan)
        athlete_means = temp.groupby(['Athlete ID', 'event_label', 'days_before_event'])[variable].mean().reset_index()
        for label, color, name in [(0, COLORS['blue'], 'Selected healthy'), (1, COLORS['red'], 'Injury labeled')]:
            profile = athlete_means[athlete_means.event_label.eq(label)].groupby('days_before_event')[variable].mean()
            ax.plot(-profile.index, profile, 'o-', color=color, label=name)
        ax.set_title(variable)
        ax.set_xlabel('Days before event')
        ax.set_xticks(range(-7, 0))
        ax.spines[['top', 'right']].set_visible(False)
        ax.grid(alpha=.15)
    axs[0, 0].legend(fontsize=8)
    fig.savefig(path, dpi=160)
    plt.close(fig)
