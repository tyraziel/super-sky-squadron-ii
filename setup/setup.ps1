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
      the_source = ""; the_target = ""}
)
            
#https://kenney.nl/media/pages/assets/space-shooter-redux/ea9a7effda-1677669442/kenney_space-shooter-redux.zip


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

    Write-Host "Creating Target Directory '$the_target'"
    $created_target_directory = New-Item -Path $the_target -ItemType "directory" -Force
    Write-Host "Created '$created_target_directory'"

    Write-Host "Copying $the_source to $created_target_directory"
    Copy-Item -Path "$the_source" -Destination "$created_target_directory" -Recurse

    #Write-Host "Deleting $the_file"
    #Remove-Item $the_file
}