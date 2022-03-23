Feature: Manage the device wallpaper

  Scenario Outline: Allow user to change the device wallpaper
    Given an english speaking user
      When the user says "<wallpaper change request>"
      Then the wallpaper should be changed

   Examples: change the wallpaper
     | wallpaper change request |
     | change the wallpaper |
     | change current wallpaper |
     | change homescreen wallpaper |
     | change background |

  Scenario Outline: Allow user to change to a named wallpaper
    Given an english speaking user
      When the user says "<wallpaper name request>"
      Then the wallpaper should be changed to green

   Examples: change the wallpaper to green
     | wallpaper name request |
     | change background to green |
     | change homescreen wallpaper to green |
