package task

import "fmt"

type TaskInt struct {
	data int
}

func (t TaskInt) WorkFunc() error {
	fmt.Println(t.data * t.data)
	return nil
}

type Task interface {
	WorkFunc() error
}
