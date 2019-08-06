import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def plot_stacked_bar(df, title, out_file, extra_text_info=None, x_axis_text_rotate=False):
    plt.clf()
    df.plot.bar(stacked=True)
    plt.title(title)
    if x_axis_text_rotate:
        plt.xticks(rotation=0)
    if extra_text_info is not None:
        plt.text(extra_text_info[0], extra_text_info[1],extra_text_info[2], fontsize=extra_text_info[3])
    plt.savefig(out_file)

def blanks_by_location(df, out_dir):
    # make blanks column
    comparitor_func = lambda row: not(row["animal_reference"])
    df["blank"] = df.apply(comparitor_func, axis=1)

    # add up animals, blanks and counter by location
    df_int = df.groupby(["location"]).sum() 
    df_int.rename(index=str, columns={"animal_reference":"animal"}, inplace=True)
    # remove extra columns
    df_int.drop(["animal_predicted", "night", "confidence", "session"], axis=1, inplace=True)
    # sort by number of blanks
    df_int.sort_values(by="blank", inplace=True, ascending=False)

    # get statistics
    total_blanks = df_int["blank"].sum()
    total_animals = df_int["animal"].sum()
    total = total_blanks + total_animals

    extra_text_info = [5, 
                       12000, 
                       "Total images:{}\nBlanks:{}\nAnimals:{}".format(total, total_blanks, total_animals),
                       10
                      ]
                        
    out_file = os.path.join(out_dir, "blanks_by_location.png")

    plot_stacked_bar(df_int, "Images by location", out_file, extra_text_info)

def blanks_by_day_night(df, out_dir):
    # make blanks column
    comparitor_func = lambda row: not(row["animal_reference"])
    df["blank"] = df.apply(comparitor_func, axis=1)

    # add up animals, blanks and counter by night
    df_int = df.groupby(["night"]).sum() 
    # rename the index
    df_int.rename(index={True:"Night", False:"Day"}, inplace=True)
    df_int.rename(index=str, columns={"animal_reference":"animal"}, inplace=True)
    # remove extra columns
    df_int.drop(["animal_predicted", "confidence", "session"], axis=1, inplace=True)
    # # sort by number of blanks
    df_int.sort_values(by="blank", inplace=True, ascending=False)

    # get statistics
    total_blanks = df_int["blank"].sum()
    total_animals = df_int["animal"].sum()
    total = total_blanks + total_animals

    extra_text_info = [1, 
                       20000, 
                       "Total images:{}\nBlanks:{}\nAnimals:{}".format(total, total_blanks, total_animals),
                       10
                      ]
    
    out_file = os.path.join(out_dir, "day-night.png")

    plot_stacked_bar(df_int, "Images by day/night", out_file, extra_text_info)

def blanks_by_camera_orientation(df, out_dir):
    # make blanks column
    comparitor_func = lambda row: not(row["animal_reference"])
    df["blank"] = df.apply(comparitor_func, axis=1)

    # make camera position column
    df_horizontal = df[df.location.str.match(pat = '(P.*)')]
    df_vertical = df[df.location.str.match(pat = '(Q.*)')]

    h_blanks = df_horizontal["blank"].sum()
    h_animal = df_horizontal["animal_reference"].sum()

    v_blanks = df_vertical["blank"].sum()
    v_animal = df_vertical["animal_reference"].sum()

    d = {'animal':pd.Series([h_animal, v_animal], index=["horizontal", "vertical"]),
         'blank':pd.Series([h_blanks, v_blanks], index=["horizontal", "vertical"])
        }

    df_plot = pd.DataFrame(d)
    
    out_file = os.path.join(out_dir, "camera_orientation.png")
    plot_stacked_bar(df_plot, "Images by camera orientation", out_file, x_axis_text_rotate=True)

def visits_by_day_night(df, out_dir):
    # work out the number of day visits
    df_day = df[df.night == False]
    df_int = df_day.groupby(["visit"]).count()
    num_day_visits = len(df_int.index)

    # number of night visits
    df_night = df[df.night == True]
    df_int = df_night.groupby(["visit"]).count()
    num_night_visits = len(df_int.index)

    s = pd.Series([num_day_visits, num_night_visits], 
                  index=["Day", "Night"])

    out_file = os.path.join(out_dir, "visits-day-night.png")
    plot_stacked_bar(s, "Visits by day/night", out_file)


def p_location_visit_duration(df, out_dir):
    # only want day time sessions in P locations
    df_day = df[(df.night == False) & df.location.str.match(pat = '(P.*)')]
    df_int = df_day.groupby(["visit"]).count()
    df_int.drop(["location", "night", "confidence", "animal_predicted", "id", "session"], axis=1, inplace=True)
    df_int.rename(index=str, columns={"animal_reference":"images"}, inplace=True)
    df_int.sort_values(by="images", inplace=True)
    extra_text = df_int.head()

    df_int.plot.hist(bins=[0,1,2,3,4,5,10,20,50,100,200])
    plt.title("Duration of visit for P locations during the day")
    plt.text(130, 8, extra_text, fontsize=10)
    out_file = os.path.join(out_dir, "p_location_visit_duration.png")
    plt.savefig(out_file)

def p_day_confidence(df, out_dir):
    # build histograms of the confidence for the true positive animal detection and the false positive animal detection
    
    # make df for false positive
    df_fp = df[(df.animal_predicted == True) & (df.animal_reference == False) & (df.night == False)]

    # make df for true positive during day
    df_tp = df[(df.animal_predicted == True) & (df.animal_reference == True) & (df.night == False)]

    fig = plt.figure()
    plt.style.use('seaborn-deep')
    ax = fig.add_subplot(111)
    df_fp[['confidence']].plot(kind='hist',bins=np.arange(0,1,0.02),rwidth=0.8, ax=ax, color='green', alpha=0.5)
    df_tp[['confidence']].plot(kind='hist',bins=np.arange(0,1,0.02),rwidth=0.8, ax=ax, color='blue', alpha=0.5)
    ax.legend(["False positive", "True positive"])
    out_file = os.path.join(out_dir, "confidence_day.png")
    plt.savefig(out_file)

def baseline_info(df, out_dir):
    blanks_by_location(df, out_dir)
    blanks_by_day_night(df, out_dir)
    blanks_by_camera_orientation(df, out_dir)
    visits_by_day_night(df, out_dir)
    p_location_visit_duration(df, out_dir)
    p_day_confidence(df, out_dir)