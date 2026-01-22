package com.example;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

public class SampleClass {

    private UserService userService = new UserService();
    private OrderRepository orderRepository;
    private List<String> names = new ArrayList<>();

    public SampleClass() {
        this.orderRepository = new OrderRepository();
    }

    public void processOrder(String orderId) {
        Order order = orderRepository.findById(orderId);
        User user = userService.getCurrentUser();

        ValidationHelper validator = new ValidationHelper();
        validator.validate(order);

        PaymentService paymentService = new PaymentService();
        paymentService.process(order.getTotal());

        userService.notifyUser(user, "Order processed");
    }

    public List<Order> getOrders() {
        return orderRepository.findAll();
    }
}
