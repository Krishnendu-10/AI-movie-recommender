package krishnendupan482.gmail.com.module1Introduction;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class  Module1IntroductionApplication implements CommandLineRunner {
    @Autowired
    PaymentService paymentServiceObj;
	public static void main(String[] args) {

        SpringApplication.run(Module1IntroductionApplication.class, args);


	}
    @Override
    public void run(String... args) throws Exception {
        // Spring safely executes this block right after startup completes
        if (paymentServiceObj != null) {
            paymentServiceObj.pay();
        } else {
            System.out.println("Dependency Injection failed: paymentServiceObj is null!");
        }
    }
}
