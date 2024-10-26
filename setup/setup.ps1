$project_root = ".."

### Create a temporary directory to do the work in
$temp_dir = ".\tmp"

Write-Host "Creating Temp Directory '$temp_dir'"
$created_temp_directory = New-Item -Path $temp_dir -ItemType "directory" -Force
Write-Host "Created '$created_temp_directory'"

Write-Host "Fetching Assets..."

$the_assets = @(
    @{the_file = "$created_temp_directory\kenney_kenney-fonts.zip"; the_url = "https://kenney.nl/media/pages/assets/kenney-fonts/1876150b34-1677661710/kenney_kenney-fonts.zip"; 
      the_source = "$created_temp_directory\Fonts\*"; the_target = "$project_root\fonts\"},
    @{the_file = "$created_temp_directory\kenney_input-prompts-pixel-16.zip"; the_url = "https://kenney.nl/media/pages/assets/input-prompts-pixel-16/a9d5de5009-1677495570/kenney_input-prompts-pixel-16.zip"; 
      the_source = "$created_temp_directory\Tilemap\tilemap_packed.png"; the_target = "$project_root\sprites\input-prompts\pixel-16\"},
    @{the_file = "$created_temp_directory\kenney_space-shooter-redux.zip"; the_url = "https://kenney.nl/media/pages/assets/space-shooter-redux/ea9a7effda-1677669442/kenney_space-shooter-redux.zip";
      the_source = @("$created_temp_directory\Spritesheet\sheet.*", "$created_temp_directory\Bonus\*.ogg"); the_target = @("$project_root\sprites\space-shooter-redux\","$project_root\sfx\space-shooter-redux\")}
)

#https://kenney.nl/media/pages/assets/simple-space/f694a6eca6-1677578143/kenney_simple-space.zip -- maybe for enemy hud stuff
#https://kenney.nl/media/pages/assets/planets/b62f72bfc7-1677495391/kenney_planets.zip

foreach ($item in $the_assets){
    $the_url = $item.the_url
    $the_file = $item.the_file
    $the_source = $item.the_source
    $the_target = $item.the_target

    Write-Host "Getting $the_url and storing it as $the_file"
    Invoke-WebRequest $the_url -OutFile $the_file
    Write-Host "Successfully retrieved $the_url as $the_file"

    Write-Host "Extracting $the_file to $created_temp_directory"
    Expand-Archive $the_file -DestinationPath $created_temp_directory -Force
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

    #Probably will leave this commented out
    #Write-Host "Deleting $the_file"
    #Remove-Item $the_file
}