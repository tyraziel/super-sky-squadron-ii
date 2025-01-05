```python
    #From my friend and pygame-ce contributor - Mzivic from the pygame-ce community
    # pos = (x, y)
    # # angle is in degrees
    # # img is input image
    # rotated_img = pygame.transform.rotozoom(img, angle, 1)
    # rotated_img_rect = rotated_img.get_rect(center=pos)
    # # surface.blit(rotated_img, rotated_img_rect)
```

From the below:
```python
# ######################################################################
# # Rotate from Center 
# # https://stackoverflow.com/questions/4183208/how-do-i-rotate-an-image-around-its-center-using-pygame
# ######################################################################
# def blitRotate(surf, image, pos, originPos, angle):

#     # offset from pivot to center
#     image_rect = image.get_rect(topleft = (pos[0] - originPos[0], pos[1]-originPos[1]))
#     offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    
#     # roatated offset from pivot to center
#     rotated_offset = offset_center_to_pivot.rotate(-angle)

#     # roatetd image center
#     rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)

#     # get a rotated image
#     rotated_image = pygame.transform.rotate(image, angle)
#     rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)

#     # rotate and blit the image
#     surf.blit(rotated_image, rotated_image_rect)
  
#     # draw rectangle around the image
#     # pygame.draw.rect(surf, (255, 0, 0), (*rotated_image_rect.topleft, *rotated_image.get_size()),2)
```