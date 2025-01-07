##### This powershell script sets up the resources that are downloadable from kenney.nl
##### It relies on creating temporary directories and then creating directorys in the project_root
##### as defined by the variable.
#####
##### UNDERSTAND WHAT THIS SCRIPT IS DOING BEFORE RUNNING IT.
##### RUN SCRIPT AT YOUR OWN RISK.
##### SCRIPT PROVIDED AS-IS.
#####
##### It's general best practice to understand any scripts that you're going to run on your computer.
##### Run script at your own risk.  This script is provided AS-IS with no warrenties or assumed liability

##### Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
##### CodeMash25\setup\setup.ps1 cannot be loaded because running scripts is disabled on this system. For more information, see about_Execution_Policies at
##### https:/go.microsoft.com/fwlink/?LinkID=135170.

$project_root = ".."

### Create a temporary directory to do the work in
$temp_dir = ".\tmp"

Write-Host "Creating Temp Directory '$temp_dir'"
$created_temp_directory = New-Item -Path $temp_dir -ItemType "directory" -Force
Write-Host "Created '$created_temp_directory'"

Write-Host "Fetching Assets..."

$the_assets = @(
    @{the_file = "$created_temp_directory\kenney_kenney-fonts.zip"; 
      the_url = "https://kenney.nl/media/pages/assets/kenney-fonts/1876150b34-1677661710/kenney_kenney-fonts.zip"; 
      the_source = "$created_temp_directory\kenney-fonts\Fonts\*"; 
      the_target = "$project_root\fonts\";
      the_temp = "kenney-fonts\"},
    @{the_file = "$created_temp_directory\kenney_input-prompts-pixel-16.zip"; 
      the_url = "https://kenney.nl/media/pages/assets/input-prompts-pixel-16/a9d5de5009-1677495570/kenney_input-prompts-pixel-16.zip"; 
      the_source = "$created_temp_directory\input-prompts\Tilemap\tilemap_packed.png"; 
      the_target = "$project_root\sprites\input-prompts\pixel-16\";
      the_temp = "input-prompts\"},
    @{the_file = "$created_temp_directory\kenney_space-shooter-redux.zip"; 
      the_url = "https://kenney.nl/media/pages/assets/space-shooter-redux/ea9a7effda-1677669442/kenney_space-shooter-redux.zip";
      the_source = @("$created_temp_directory\space-shooter-redux\Bonus\*.ogg"); 
      the_target = @("$project_root\sfx\space-shooter-redux\");
      the_temp = "space-shooter-redux\"},
    # @{the_file = "$created_temp_directory\kenney_space-shooter-redux.zip"; 
    #   the_url = "https://kenney.nl/media/pages/assets/space-shooter-redux/ea9a7effda-1677669442/kenney_space-shooter-redux.zip";
    #   the_source = @("$created_temp_directory\space-shooter-redux\Spritesheet\sheet.*", "$created_temp_directory\space-shooter-redux\Bonus\*.ogg"); 
    #   the_target = @("$project_root\sprites\space-shooter-redux\", "$project_root\sfx\space-shooter-redux\");
    #   the_temp = "space-shooter-redux\"},
    @{the_file = "$created_temp_directory\kenney_space-shooter-redux.zip"; 
      the_url = "https://kenney.nl/media/pages/assets/space-shooter-redux/ea9a7effda-1677669442/kenney_space-shooter-redux.zip";
      the_source = @("$created_temp_directory\space-shooter-redux\Bonus\*.ogg"); 
      the_target = @("$project_root\sfx\space-shooter-redux\");
      the_temp = "space-shooter-redux\"},
    @{the_file = "$created_temp_directory\kenney_pixel-shmup.zip"; 
      the_url = "https://kenney.nl/media/pages/assets/pixel-shmup/899a89fc6e-1677495782/kenney_pixel-shmup.zip";
      the_source = @("$created_temp_directory\pixel-shmup\Tilemap\*_packed.png"); 
      the_target = @("$project_root\sprites\pixel-shmup\");
      the_temp = "pixel-shmup\"},
    @{the_file = "$created_temp_directory\kenney_ui-pack.zip"; 
      the_url = "https://kenney.nl/media/pages/assets/ui-pack/008d5df50e-1718203990/kenney_ui-pack.zip";
      the_source = @("$created_temp_directory\ui-pack\PNG\Grey\Default\button_square_flat.png"); 
      the_target = @("$project_root\sprites\ui-pack\grey\default\");
      the_temp = "ui-pack\"}
)

#https://kenney.nl/media/pages/assets/music-jingles/acd2ca8b8f-1677590399/kenney_music-jingles.zip
#https://kenney.nl/media/pages/assets/digital-audio/cd01f555fb-1677590265/kenney_digital-audio.zip
#https://kenney.nl/media/pages/assets/impact-sounds/6eeae25aef-1677589768/kenney_impact-sounds.zip

#shttps://kenney.nl/media/pages/assets/sci-fi-sounds/81d6323e0a-1677589334/kenney_sci-fi-sounds.zip
#https://kenney.nl/media/pages/assets/interface-sounds/f3134a7c4c-1677589452/kenney_interface-sounds.zip
#https://kenney.nl/media/pages/assets/rpg-audio/20c02ef17c-1677590336/kenney_rpg-audio.zip
#https://kenney.nl/media/pages/assets/ui-audio/6ecc8f60b2-1677590494/kenney_ui-audio.zip

#https://kenney.nl/media/pages/assets/voiceover-pack-fighter/08afb354ef-1677589837/kenney_voiceover-pack-fighter.zip
#https://kenney.nl/media/pages/assets/voiceover-pack/73832acf09-1677589897/kenney_voiceover-pack.zip


#https://kenney.nl/media/pages/assets/simple-space/f694a6eca6-1677578143/kenney_simple-space.zip -- maybe for enemy hud stuff
#https://kenney.nl/media/pages/assets/planets/b62f72bfc7-1677495391/kenney_planets.zip
#https://kenney.nl/media/pages/assets/ranks-pack/dbfb992998-1677578852/kenney_ranks-pack.zip
#https://kenney.nl/media/pages/assets/emotes-pack/a3823d6799-1677578798/kenney_emotes-pack.zip
#https://kenney.nl/media/pages/assets/space-shooter-extension/57049efd94-1677693518/kenney_space-shooter-extension.zip
#https://kenney.nl/media/pages/assets/smoke-particles/adfa60d27d-1677695171/kenney_smoke-particles.zip


#https://kenney.nl/media/pages/assets/pixel-shmup/899a89fc6e-1677495782/kenney_pixel-shmup.zip
#https://kenney.nl/media/pages/assets/medals/68269b9e9e-1677668150/kenneymedals.zip


foreach ($item in $the_assets){
    $the_url = $item.the_url
    $the_file = $item.the_file
    $the_source = $item.the_source
    $the_target = $item.the_target
    $the_temp = $item.the_temp

    Write-Host "Creating Temp Sub-Directory '$created_temp_directory\$the_temp'"
    $created_temp_sub_directory = New-Item -Path "$created_temp_directory\$the_temp" -ItemType "directory" -Force
    Write-Host "Created '$created_temp_sub_directory'"

    Write-Host "Getting $the_url and storing it as $the_file"
    Invoke-WebRequest $the_url -OutFile $the_file
    Write-Host "Successfully retrieved $the_url as $the_file"

    Write-Host "Extracting $the_file to $created_temp_sub_directory"
    Expand-Archive $the_file -DestinationPath $created_temp_sub_directory -Force
    Write-Host "Extraction Completed"

    if($the_source -is [array] -and $the_target -is [array] ){
      for ($i = 0; $i -lt $the_source.Count -and $i -lt $the_target.Count; $i++){
        $item_source = $the_source[$i]
        $item_target = $the_target[$i]

        Write-Host "Creating Target Directory '$item_target'"
        $created_target_directory = New-Item -Path $item_target -ItemType "directory" -Force
        Write-Host "Created '$created_target_directory'"

        Write-Host "Copying $item_source to $created_target_directory)"
        Copy-Item -Path "$item_source" -Destination "$created_target_directory" -Recurse
      }
    }
    else{
      Write-Host "Creating Target Directory '$the_target'"
      $created_target_directory = New-Item -Path $the_target -ItemType "directory" -Force
      Write-Host "Created '$created_target_directory'"

      Write-Host "Copying $the_source to $created_target_directory"
      Copy-Item -Path "$the_source" -Destination "$created_target_directory" -Recurse
    }
}

###Copy etc assets into the proper locations
Copy-Item -Path "../etc/ships_sheet.xml" -Destination "../sprites/pixel-shmup/ships_sheet.xml"
Copy-Item -Path "../etc/tilemap_sheet.xml" -Destination "../sprites/input-prompts/pixel-16/tilemap_sheet.xml"
Copy-Item -Path "../etc/tiles_sheet.xml" -Destination "../sprites/pixel-shmup/tiles_sheet.xml"