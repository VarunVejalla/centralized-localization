#include <stdio.h>
#include <stdlib.h>

#define OLEV 600       /* in feets/minute */
#define MAXALTDIFF 600 /* max altitude difference in feet */
#define MINSEP 300     /* min separation in feet */
#define NOZCROSS 100   /* in feet */

typedef int bool;

int Cur_Vertical_Sep;
bool High_Confidence;
bool Two_of_Three_Reports_Valid;

int Own_Tracked_Alt;
int Own_Tracked_Alt_Rate;
int Other_Tracked_Alt;

int Alt_Layer_Value; /* 0, 1, 2, 3 */
int Positive_RA_Alt_Thresh[4];

int Up_Separation;
int Down_Separation;

/* state variables */
int Other_RAC; /* NO_INTENT, DO_NOT_CLIMB, DO_NOT_DESCEND */
#define NO_INTENT 0
#define DO_NOT_CLIMB 1
#define DO_NOT_DESCEND 2

int Other_Capability; /* TCAS_TA, OTHER */
#define TCAS_TA 1
#define OTHER 2

int Climb_Inhibit; /* true/false */

#define UNRESOLVED 0
#define UPWARD_RA 1
#define DOWNWARD_RA 2

int main( int argc, char *argv[])
{
    int alt_sep;
    int ALIM_value; /* result of ALIM() */
    int inhibit_biased_climb_value; /* result of Inhibit_Biased_Climb() */
    bool own_below_threat; /* result of Own_Below_Threat() */
    bool own_above_threat; /* result of Own_Above_Threat() */
    int upward_preferred; 
    bool non_crossing_biased_climb; /* result of Non_Crossing_Biased_Climb() */
    bool non_crossing_biased_descend; /* result of Non_Crossing_Biased_Descend() */
    bool enabled, tcas_equipped, intent_not_known;
    bool need_upward_RA, need_downward_RA;

    if (argc < 13)
    {
        fprintf(stdout, "Error: Command line arguments are\n");
        fprintf(stdout, "Cur_Vertical_Sep, High_Confidence, Two_of_Three_Reports_Valid\n");
        fprintf(stdout, "Own_Tracked_Alt, Own_Tracked_Alt_Rate, Other_Tracked_Alt\n");
        fprintf(stdout, "Alt_Layer_Value, Up_Separation, Down_Separation\n");
        fprintf(stdout, "Other_RAC, Other_Capability, Climb_Inhibit\n");
        exit(1);
    }
    /* initialize */
    Positive_RA_Alt_Thresh[0] = 400;
    Positive_RA_Alt_Thresh[1] = 500;
    Positive_RA_Alt_Thresh[2] = 640;
    Positive_RA_Alt_Thresh[3] = 740;
    
    Cur_Vertical_Sep = atoi(argv[1]);
    High_Confidence = atoi(argv[2]);
    Two_of_Three_Reports_Valid = atoi(argv[3]);
    Own_Tracked_Alt = atoi(argv[4]);
    Own_Tracked_Alt_Rate = atoi(argv[5]);
    Other_Tracked_Alt = atoi(argv[6]);
    Alt_Layer_Value = atoi(argv[7]);
    Up_Separation = atoi(argv[8]);
    Down_Separation = atoi(argv[9]);
    Other_RAC = atoi(argv[10]);
    Other_Capability = atoi(argv[11]);
    Climb_Inhibit = atoi(argv[12]);

    /* Inlined version of ALIM() */
    ALIM_value = Positive_RA_Alt_Thresh[Alt_Layer_Value];

    /* Inlined version of Inhibit_Biased_Climb() */
    inhibit_biased_climb_value = (Climb_Inhibit ? Up_Separation + NOZCROSS : Up_Separation);

    /* Inlined version of Own_Below_Threat() and Own_Above_Threat() */
    own_below_threat = (Own_Tracked_Alt < Other_Tracked_Alt);
    own_above_threat = (Other_Tracked_Alt < Own_Tracked_Alt);

    /* Inlined version of Non_Crossing_Biased_Climb() */
    if (inhibit_biased_climb_value > Down_Separation)
        upward_preferred = 1;
    else
        upward_preferred = 0;
    if (upward_preferred)
    {
        non_crossing_biased_climb = (!own_below_threat) || (own_below_threat && (!(Down_Separation >= ALIM_value)));
    }
    else
    {
        non_crossing_biased_climb = own_above_threat && (Cur_Vertical_Sep >= MINSEP) && (Up_Separation >= ALIM_value);
    }

    /* Inlined version of Non_Crossing_Biased_Descend() */
    if (inhibit_biased_climb_value > Down_Separation)
    {
        non_crossing_biased_descend = own_below_threat && (Cur_Vertical_Sep >= MINSEP) && (Down_Separation >= ALIM_value);
    }
    else
    {
        non_crossing_biased_descend = (!own_above_threat) || (own_above_threat && (Up_Separation >= ALIM_value));
    }

    /* Inlined version of alt_sep_test() */
    enabled = High_Confidence && (Own_Tracked_Alt_Rate <= OLEV) && (Cur_Vertical_Sep > MAXALTDIFF);
    tcas_equipped = (Other_Capability == TCAS_TA);
    intent_not_known = Two_of_Three_Reports_Valid && (Other_RAC == NO_INTENT);

    alt_sep = UNRESOLVED;

    if (enabled && ((tcas_equipped && intent_not_known) || !tcas_equipped))
    {
        need_upward_RA = non_crossing_biased_climb && own_below_threat;
        need_downward_RA = non_crossing_biased_descend && own_above_threat;
        if (need_upward_RA && need_downward_RA)
            /* unreachable: requires Own_Below_Threat and Own_Above_Threat
               to both be true - that requires Own_Tracked_Alt < Other_Tracked_Alt
               and Other_Tracked_Alt < Own_Tracked_Alt, which isn't possible */
            alt_sep = UNRESOLVED;
        else if (need_upward_RA)
            alt_sep = UPWARD_RA;
        else if (need_downward_RA)
            alt_sep = DOWNWARD_RA;
        else
            alt_sep = UPWARD_RA; // Mutant: changed UNRESOLVED to UPWARD_RA
    }

    fprintf(stdout, "%d\n", alt_sep);
    exit(0);
}
