import React, { Component } from 'react';
import Button from '@material-ui/core/Button';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';

const DashboardBar = () => {
  const [open, setOpen] = React.useState(true);
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
   <>
    <Button aria-controls="simple-menu" aria-haspopup="true" onClick={handleClick} color="inherit">
      CPU
    </Button>
    <Menu
      id="simple-menu"
      anchorEl={anchorEl}
      keepMounted
      open={Boolean(anchorEl)}
      onClose={handleClose}
    >
      <MenuItem onClick={handleClose}>MenuItem 1</MenuItem>
      <MenuItem onClick={handleClose}>MenuItem 2</MenuItem>
      <MenuItem onClick={handleClose}>MenuItem 3</MenuItem>
    </Menu>
    <Button aria-controls="simple-menu" aria-haspopup="true" color="inherit">
      Memory
    </Button>
    <Button aria-controls="simple-menu" aria-haspopup="true" color="inherit">
      IO
    </Button>
   </>
  );
}

export default DashboardBar;
