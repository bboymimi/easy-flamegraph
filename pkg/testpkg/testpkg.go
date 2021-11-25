package testpkg

import (
	"fmt"
	"time"

	"github.com/bboymimi/easy-flamegraph/pkg/workers"
)

type procs struct {
	pool workers.Pool
}

func NewProcs(pool workers.Pool) *procs {
	var procs = &procs{pool: pool}
	return procs
}

func (p *procs) Start() {
	// Push the task items into the queue
	workCount := 4
	for i := 0; i < workCount; i++ {
		p.pool.Send(p)
	}
}

func (p *procs) Test() {
	go func() {
		for {
			time.Sleep(time.Second)
			p.Start()
		}
	}()
}

func (p *procs) WorkFunc() error {
	fmt.Println("test workfunction!!")
	return nil
}
