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
