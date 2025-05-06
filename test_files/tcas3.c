#include <stdio.h>
#include <stdlib.h>

#define OLEV       600
#define MAXALTDIFF 600
#define MINSEP     300
#define NOZCROSS   100

typedef int bool;

#define NO_INTENT 0
#define DO_NOT_CLIMB 1
#define DO_NOT_DESCEND 2

#define TCAS_TA 1
#define OTHER 2

#define UNRESOLVED 0
#define UPWARD_RA 1
#define DOWNWARD_RA 2

int main(int argc, char *argv[])
{
    int Cur_Vertical_Sep;
    bool High_Confidence;
    bool Two_of_Three_Reports_Valid;

    int Own_Tracked_Alt;
    int Own_Tracked_Alt_Rate;
    int Other_Tracked_Alt;

    int Alt_Layer_Value;
    int Positive_RA_Alt_Thresh[4];

    int Up_Separation;
    int Down_Separation;

    int Other_RAC;
    int Other_Capability;
    int Climb_Inhibit;

    if (argc < 13)
    {
        fprintf(stdout, "Error: Command line arguments are\n");
        fprintf(stdout, "Cur_Vertical_Sep, High_Confidence, Two_of_Three_Reports_Valid\n");
        fprintf(stdout, "Own_Tracked_Alt, Own_Tracked_Alt_Rate, Other_Tracked_Alt\n");
        fprintf(stdout, "Alt_Layer_Value, Up_Separation, Down_Separation\n");
        fprintf(stdout, "Other_RAC, Other_Capability, Climb_Inhibit\n");
        exit(1);
    }

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

    int alt_sep = UNRESOLVED;
    bool enabled = High_Confidence && (Own_Tracked_Alt_Rate <= OLEV) && (Cur_Vertical_Sep > MAXALTDIFF);
    bool tcas_equipped = Other_Capability == TCAS_TA;
    bool intent_not_known = Two_of_Three_Reports_Valid && Other_RAC == NO_INTENT;

    if (enabled && ((tcas_equipped && intent_not_known) || !tcas_equipped))
    {
        int alim = Positive_RA_Alt_Thresh[Alt_Layer_Value];
        int inhibit_biased_climb = (Climb_Inhibit ? Up_Separation + NOZCROSS : Up_Separation);

        bool upward_preferred = inhibit_biased_climb > Down_Separation;
        bool own_below_threat = Own_Tracked_Alt < Other_Tracked_Alt;
        bool own_above_threat = Other_Tracked_Alt < Own_Tracked_Alt;

        bool need_upward_RA;
        if (upward_preferred)
        {
            need_upward_RA = !own_below_threat || (own_below_threat && !(Down_Separation >= alim));
        }
        else
        {
            need_upward_RA = own_above_threat && (Cur_Vertical_Sep >= MINSEP) && (Up_Separation >= alim);
        }
        need_upward_RA = need_upward_RA && own_below_threat;

        bool need_downward_RA;
        if (upward_preferred)
        {
            need_downward_RA = own_below_threat && (Cur_Vertical_Sep >= MINSEP) && (Down_Separation >= alim);
        }
        else
        {
            need_downward_RA = own_above_threat && (Up_Separation >= alim); // MUTANT line
        }
        need_downward_RA = need_downward_RA && own_above_threat;

        if (need_upward_RA && need_downward_RA)
        {
            alt_sep = UNRESOLVED;
        }
        else if (need_upward_RA)
        {
            alt_sep = UPWARD_RA;
        }
        else if (need_downward_RA)
        {
            alt_sep = DOWNWARD_RA;
        }
        else
        {
            alt_sep = UNRESOLVED;
        }
    }

    fprintf(stdout, "%d\n", alt_sep);
    return 0;
}
