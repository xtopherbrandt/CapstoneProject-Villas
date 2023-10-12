import ListItem from '@mui/material/ListItem';
import IconButton from '@mui/material/IconButton';
import ListItemText from '@mui/material/ListItemText';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import moment from 'moment';
import { ButtonGroup, Stack, Typography } from '@mui/material';
import React from 'react';
import CheckIn from './checkIn';

function UnitDetail( props ){

  const [crudMode, setcrudMode] = React.useState("create");
  
  if (props.unitStatus !== 'Available' ){
    setcrudMode("read");
  }

  if (crudMode !== 'read' ){
    return (
      <ListItem key={props.key}>
        <Stack key={props.unitNumber} dddd>
          <CheckIn unitNumber={props.unitNumber} setDirtyFlag={props.setDirtyFlag} />
          <ListItemText 
            primary={"Unit #" + props.unitNumber} 
            secondary={props.unitStatus}
          />
        </Stack>
          
      </ListItem>
    );
  }
  else{
    return(
      <ListItem 
        key={props.key}
        secondaryAction={
          <ButtonGroup aria-aria-label='cancel or modify button group'>
            <IconButton edge="end" aria-label='cancel' onClick={() => { props.cancelCheckInHandler(props.cancelCheckInLink, props.setDirtyFlag );}}>
              <DeleteIcon/>
            </IconButton>
            <IconButton edge="end" aria-label='modify' onClick={() => { props.modifyCheckInHandler(props.modifyCheckInLink, props.unitNumber, props.checkOutDate, props.vehicleLicense, props.setDirtyFlag );}}>
              <EditIcon/>
            </IconButton>
          </ButtonGroup>
        }>
          <ListItemText 
            primary={"Unit #" + props.unitNumber}
            secondary={
              <React.Fragment>
                <Typography
                  sx={{ display: 'inline'}}
                  component="span"
                  variant="body2"
                  color="text.primary">
                    {props.unitStatus}
                  </Typography>
                  {" : " + moment(props.checkInDate).format('LL') + " - " + moment(props.checkOutDate).format('LL')}
              </React.Fragment>
            }
          />

        </ListItem>
      );
    }
  }

  export default UnitDetail;