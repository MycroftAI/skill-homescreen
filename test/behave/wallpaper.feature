Feature: Manage the device wallpaper

  Scenario Outline: Allow user to change the device wallpaper
    Given an english speaking user
      When the user says "change the wallpaper"
      Then the wallpaper should be changed

   Examples: change the wallpaper
     | change the wallpaper |
     | change the wallpaper |
     | change current wallpaper |
     | change homescreen wallpaper |
