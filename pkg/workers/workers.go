package workers

import (
	"fmt"

	task "github.com/bboymimi/easy-flamegraph/pkg/tasks"
)

type pool struct {
	in        chan task.Task
	out       chan interface{}
	nrWorkers int
	twait     chan int
	pwait     chan bool
}

type Pool interface {
	Send(task task.Task)
	Start() Pool
	Stop()
	Wait() error
}

func (p *pool) Start() Pool {
	p.pwait <- true
	for i := 0; i <= p.nrWorkers; i++ {
		go func(i int) {
			p.twait <- i
			defer func() {
				<-p.twait
			}()
			for t := range p.in {
				fmt.Println("goroutine", i, "in loop")
				if err := t.WorkFunc(); err != nil {
					return
				}
			}
			fmt.Println("goroutine:", i)
		}(i)
	}
	return p
}

func (p *pool) Stop() {
}

func (p *pool) Send(task task.Task) {
	p.in <- task
}

func (p *pool) Wait() error {
	for len(p.twait) > 0 || <-p.pwait {
		fmt.Println("waiting")
	}
	return nil
}

func NewPool(nrWorkers int) Pool {
	var p = &pool{
		in:        make(chan task.Task, nrWorkers),
		out:       nil,
		nrWorkers: nrWorkers,
		twait:     make(chan int, nrWorkers),
		pwait:     make(chan bool, 1),
	}
	return p
}
